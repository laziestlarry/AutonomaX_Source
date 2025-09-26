# Intake Google Drive Resources (CSV)

You can include Google Drive folders/files as links in CSVs and feed them into intake/blueprint.

CSV example (place under `repos/drive_links.csv`):

```
name,url,desc,tags,score
Brand Kit,https://drive.google.com/drive/folders/BRAND-KIT-ID,Logos/palette/voice,branding,90
YouTube Shorts,https://drive.google.com/drive/folders/YT-SHORTS-ID,Scripts + voiceovers + thumbnails,video,88
```

Then run:

- Intake for Agents suggestions:
  - `./ops/intake_inventory.sh --filelist repos/drive_links.csv --label drive`
- Add to blueprint (combine with repo CSVs):
  - `./ops/generate_blueprint.sh repos repos 20`

Tips
- For per-file links, add `https://drive.google.com/file/d/FILE_ID/view` URLs similarly.
- For full listings, use Drive API or Apps Script to export a CSV of file URLs (optional; not required for quick start).
- Links are recorded as `kind=link` during intake (no download).

