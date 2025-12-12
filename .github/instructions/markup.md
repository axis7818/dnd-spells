# Markup Instructions

Format: `{@<cmd> <text>|<source>}` should become just `<text>`.
Format: `{@<cmd> <text> [kind]|<source>}` should become just `<text>`.

Example conversions:

- `A willing creature you touch shape-shifts, along with everything it's wearing and carrying, into a misty cloud for the duration. The spell ends on the target if it drops to 0 {@variantrule Hit Points|XPHB} or if it takes a {@action Magic|XPHB} action to end the spell on itself.` should be `A willing creature you touch shape-shifts, along with everything it's wearing and carrying, into a misty cloud for the duration. The spell ends on the target if it drops to 0 Hit Points or if it takes a Magic action to end the spell on itself.`
- `An aura radiates from you in a 30-foot {@variantrule Emanation [Area of Effect]|XPHB|Emanation} for the duration. While in the aura, you and your allies have {@variantrule Resistance|XPHB} to Poison damage and {@variantrule Advantage|XPHB} on saving throws to avoid or end effects that include the {@condition Blinded|XPHB}, {@condition Charmed|XPHB}, {@condition Deafened|XPHB}, {@condition Frightened|XPHB}, {@condition Paralyzed|XPHB}, {@condition Poisoned|XPHB}, or {@condition Stunned|XPHB} condition.` should be `An aura radiates from you in a 30-foot Emanation for the duration. While in the aura, you and your allies have Resistance to Poison damage and Advantage on saving throws to avoid or end effects that include the Blinded, Charmed, Deafened, Frightened, Paralyzed, Poisoned, or Stunned condition.`
