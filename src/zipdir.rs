use std::fs::File;
use std::io::{Seek, Write};
use std::path::{Path, PathBuf};

use anyhow::{Context, Result};
use walkdir::WalkDir;
use zip::write::FileOptions;

fn zip_name_from_path(root: &Path, path: &Path) -> Result<String> {
    let rel = path
        .strip_prefix(root)
        .with_context(|| format!("strip prefix {} from {}", root.display(), path.display()))?;

    let parts: Vec<String> = rel
        .components()
        .map(|c| c.as_os_str().to_string_lossy().to_string())
        .collect();
    Ok(parts.join("/"))
}

pub fn zip_dir_contents<W: Write + Seek>(dir: &Path, writer: &mut W) -> Result<()> {
    let mut zip = zip::ZipWriter::new(writer);
    let opts = FileOptions::default().compression_method(zip::CompressionMethod::Deflated);

    let mut files: Vec<PathBuf> = Vec::new();
    for entry in WalkDir::new(dir).into_iter().filter_map(|e| e.ok()) {
        if entry.file_type().is_file() {
            files.push(entry.path().to_path_buf());
        }
    }
    files.sort();

    for path in files {
        let name = zip_name_from_path(dir, &path)?;
        zip.start_file(name, opts)?;
        let mut f = File::open(&path).with_context(|| format!("open {}", path.display()))?;
        std::io::copy(&mut f, &mut zip).with_context(|| format!("zip {}", path.display()))?;
    }

    zip.finish()?;
    Ok(())
}
