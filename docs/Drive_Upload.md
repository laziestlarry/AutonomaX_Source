# Upload artifacts to Google Drive (via rclone)

- Install rclone: https://rclone.org/install/
- Configure a Drive remote (once):
  - `rclone config` → New remote → Name: `drive` → Type: `drive` → follow auth

Upload our key artifacts (inventory, blueprints, delivery evidence):

```
./ops/upload_to_drive.sh drive:AutonomaX \
  data_room/inventory \
  data_room/blueprints \
  revenue_sprint_lite_payoneer/delivery
```

This mirrors local directories to Drive folders for a quick handoff or backup.

