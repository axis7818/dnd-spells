use std::fs;
use std::io::{self, Write};
use std::path::{Path, PathBuf};

use anyhow::{bail, Context, Result};
use clap::Parser;
use serde_json::Value;

mod convert;
mod markup;
mod zipdir;

#[derive(Parser, Debug)]
#[command(
    name = "dnd-spells",
    about = "Convert a JSON array of D&D spells to Obsidian-friendly markdown."
)]
struct Args {
    /// Path to a JSON file containing a list/array of spells.
    #[arg(long, default_value = "examples/all-spells.json")]
    input: PathBuf,

    /// Directory to write markdown files into.
    #[arg(long = "output-dir", default_value = "output/spells")]
    output_dir: PathBuf,

    /// Do not create the spells-<version>.zip archive.
    #[arg(long = "no-zip")]
    no_zip: bool,
}

fn slugify_filename(name: &str) -> String {
    // Match Python: _FILENAME_SAFE_RE = r"[^A-Za-z0-9_' -]+"; replace with "-"; strip '-'
    let re = regex::Regex::new(r"[^A-Za-z0-9_' -]+").expect("valid regex");
    let safe = re.replace_all(name, "-");
    let safe = safe.trim_matches('-').to_string();
    if safe.is_empty() {
        "spell".to_string()
    } else {
        safe
    }
}

fn read_spells(path: &Path) -> Result<Vec<Value>> {
    let raw = fs::read_to_string(path).with_context(|| format!("read input {}", path.display()))?;
    let value: Value = serde_json::from_str(&raw).context("parse JSON")?;
    match value {
        Value::Array(items) => Ok(items),
        _ => bail!("input JSON must be an array of spells"),
    }
}

fn write_version_file(output_dir: &Path) -> Result<()> {
    let version = env!("CARGO_PKG_VERSION");
    fs::write(output_dir.join("_version.txt"), version)
        .with_context(|| "write _version.txt".to_string())?;
    Ok(())
}

fn run(args: Args) -> Result<()> {
    fs::create_dir_all(&args.output_dir)
        .with_context(|| format!("create output dir {}", args.output_dir.display()))?;

    let spells = read_spells(&args.input)?;

    for spell in spells {
        let name = spell
            .get("name")
            .and_then(|v| v.as_str())
            .unwrap_or("unnamed");
        let out_path = args
            .output_dir
            .join(format!("{}.md", slugify_filename(name)));

        let md = convert::spell_to_markdown(&spell);
        fs::write(&out_path, md).with_context(|| format!("write {}", out_path.display()))?;
    }

    write_version_file(&args.output_dir)?;

    if !args.no_zip {
        let version = env!("CARGO_PKG_VERSION");
        let zip_name = format!("spells-{}.zip", version);
        let zip_file = fs::File::create(&zip_name)
            .with_context(|| format!("create {}", zip_name))?;
        let mut writer = io::BufWriter::new(zip_file);
        zipdir::zip_dir_contents(&args.output_dir, &mut writer)?;
        writer.flush().ok();
    }

    Ok(())
}

fn main() {
    let args = Args::parse();
    if let Err(err) = run(args) {
        eprintln!("{:#}", err);
        std::process::exit(1);
    }
}
