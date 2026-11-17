# Design system

**Identity:** "forge". Dark charcoal surfaces, an ember accent for effort, and one colour per discipline. Dark is the default; light is optional (Profile > App).

| Token | Dark | Light | Use |
|---|---|---|---|
| bg | #0D1014 | #F4F6F8 | Page background |
| card | #161B21 | #FFFFFF | Cards |
| card2 | #1E252D | #EEF1F4 | Tiles, inputs, ring tracks |
| line | #2A323C | #E1E6EB | Borders, grid lines |
| text | #E8EDF2 | #14202B | Primary text |
| mut | #8C99A6 | #5F6B78 | Secondary text |
| accent (ember) | #FF7A3D | #E2601F | Primary actions, running |
| teal | #2EC4B6 | #0F8C80 | Strength, protein |
| swim | #4DA3FF | #1565C0 | Swimming, water |
| bike | #B07CFF | #6A3FC4 | Cycling, bricks |
| hyrox | #FFD34D | #9A7400 | HYROX |
| ok / warn / bad | #3DDC84 / #F5B841 / #FF5C5C | #2E7D32 / #B26A00 / #C62828 | Status |

- **Typography:** the system font (Roboto on Android). Titles 20 to 26 px, weight 800, slight negative tracking; body 14 px with 1.35 line height; labels 12 px.
- **Components** (`app/lib/ui.dart`): Section (card with an optional discipline stripe), Pill, KV row, Bar, Ring, StatTile and TileRow, BarChart, LineChart (with a target line), NumField and TextBox (save as you type), Scale5 (1 to 5 picker), EmptyState.
- **Navigation:** five tabs: Home, Training, Nutrition, Progress, Profile. Workouts open full screen with the next and skip actions at the bottom (thumb reach).
- **States:**
  - Empty: an EmptyState, or "No data yet" in charts.
  - Loading: a sync spinner in the app bar.
  - Error: a snackbar plus the sync note, with changes kept in the outbox.
  - Offline: a cloud-off icon.
  - Pending plan: a banner on Home.
- **Touch targets:** 48 dp minimum, and 56 dp for the main Start button.
