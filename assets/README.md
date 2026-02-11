# Asset Images for SWGOH Automation

This directory contains reference images used by the automation bot for game element recognition. The bot uses computer vision to identify and interact with game elements based on these reference images.

## Directory Structure

```
assets/
├── README.md                 # This file
├── game_icon.png            # Game app icon
├── energy_button.png        # Energy management button
├── start_battle.png         # Start battle button
├── auto_button.png          # Auto battle toggle
├── claim_rewards.png        # Claim rewards button
├── confirm_button.png       # Confirm action button
├── close_button.png         # Close/exit button
├── back_button.png          # Navigate back button
├── characters/              # Character portraits
├── stages/                  # Battle stage buttons
├── challenges/              # Challenge buttons
└── ui_elements/             # General UI elements
```

## Required Images

### Core UI Elements
- **game_icon.png** - Main game icon for detecting if game is running
- **energy_button.png** - Energy management/access button
- **start_battle.png** - Start battle confirmation button
- **auto_button.png** - Toggle for auto-battle mode
- **claim_rewards.png** - Claim/collect rewards button
- **confirm_button.png** - Yes/confirm action button
- **close_button.png** - X/close window button
- **back_button.png** - Navigate back arrow/button

### Energy Management
- **cantina_refill.png** - Cantina energy refill option
- **regular_refill.png** - Regular energy refill option
- **fleet_refill.png** - Fleet energy refill option

### Battle Navigation
- **cantina_battles.png** - Cantina battles mode button
- **regular_battles.png** - Regular battles mode button
- **fleet_battles.png** - Fleet battles mode button
- **team_setup.png** - Team setup/configuration button
- **confirm_team.png** - Confirm team selection button

### Daily Activities
- **daily_login.png** - Daily login rewards popup
- **claim_daily.png** - Claim daily reward button
- **next_day.png** - Next day/continue button
- **challenges_button.png** - Challenges access button
- **daily_challenges.png** - Daily challenges tab
- **guild_challenges.png** - Guild challenges tab
- **fleet_challenges.png** - Fleet challenges tab
- **cantina_challenges.png** - Cantina challenges tab
- **guild_button.png** - Guild access button
- **guild_donate.png** - Guild donation button
- **guild_raids.png** - Guild raids access
- **collection_button.png** - Collection access button

### Guild Activities
- **donate_credits.png** - Donate credits button
- **donate_materials.png** - Donate materials button
- **donate_ship_parts.png** - Donate ship parts button
- **join_raid.png** - Join raid button
- **start_raid.png** - Start raid button

### Reward Collection
- **collect_button.png** - General collect button
- **gift_box.png** - Gift box/notification icon
- **notification.png** - Notification indicator
- **ok_button.png** - OK/acknowledge button
- **continue.png** - Continue/next button

## Character Images (assets/characters/)

Character portraits are used for team selection. Images should be:
- **Size**: 64x64 to 128x128 pixels
- **Format**: PNG with transparent background
- **Content**: Clear character portrait from the character selection screen
- **Naming**: Use lowercase with underscores (e.g., `jedi_knight_luke.png`)

### Essential Characters for Common Teams
- `jedi_knight_luke.png`
- `old_daka.png`
- `acolyte.png`
- `ig_86.png`
- `talia.png`
- `jedi_knight_anakin.png`
- `ahsoka_tano.png`
- `barriss_offee.png`
- `mace_windu.png`
- `kit_fisto.png`
- `ghost.png`
- `phantom.png`
- `ebon_hawk.png`
- `millennium_falcon.png`
- `u_wing.png`

## Stage Images (assets/stages/)

Battle stage buttons for automated farming. Images should be:
- **Size**: 100x50 to 200x100 pixels
- **Format**: PNG with transparent background
- **Content**: Stage button from battle selection screen
- **Naming**: Stage identifier (e.g., `1-a.png`, `2-b.png`)

### Common Farming Stages
- `1-a.png` - Light Side 1-A
- `1-b.png` - Light Side 1-B
- `2-a.png` - Light Side 2-A
- `2-b.png` - Light Side 2-B
- `3-a.png` - Light Side 3-A
- `3-b.png` - Light Side 3-B
- `cantina_1.png` - Cantina Battle 1
- `cantina_2.png` - Cantina Battle 2
- `fleet_1.png` - Fleet Battle 1
- `fleet_2.png` - Fleet Battle 2

## Challenge Images (assets/challenges/)

Challenge buttons for daily activities:
- **Size**: 150x75 pixels
- **Format**: PNG with transparent background
- **Naming**: Challenge name with underscores

### Example Challenge Images
- `daily_challenges.png`
- `guild_raid.png`
- `fleet_challenges.png`
- `cantina_challenges.png`

## UI Elements (assets/ui_elements/)

General UI elements for navigation:
- **menu_button.png** - Main menu button
- **settings_button.png** - Settings gear icon
- **shop_button.png** - Shop/store button
- **datacron_button.png** - Datacron button
- `squad_arena.png` - Squad arena button
- `fleet_arena.png` - Fleet arena button

## Image Guidelines

### Quality Requirements
- **Resolution**: Clear and sharp, no blur
- **Lighting**: Consistent lighting conditions
- **Cropping**: Tight crop around the element
- **Background**: Transparent or consistent background

### Screenshot Tips
1. **Take screenshots at the same resolution** as your game display
2. **Use consistent emulator settings** (zoom level, UI scale)
3. **Capture elements in their default state** (not highlighted/pressed)
4. **Avoid capturing animated elements** - wait for static state
5. **Use the same game version** as you'll be automating

### Image Preparation
```bash
# Example using ImageMagick for optimization
convert character.png -resize 80x80 -transparent white character_optimized.png
```

## Testing Images

After adding new images, test them with the bot:

1. **Place images in appropriate directories**
2. **Run the bot in debug mode**
3. **Check logs for recognition confidence**
4. **Adjust images if recognition fails**

### Debug Commands
```python
# Test image recognition
python -c "
from main import SWGOHAutomator
automator = SWGOHAutomator()
result = automator.find_image_on_screen('assets/your_image.png')
print(f'Found at: {result}')
"
```

## Updating Images

When the game updates:
1. **Check for UI changes** in the new version
2. **Retake affected screenshots**
3. **Test recognition with new images**
4. **Update asset directory** if needed

## Troubleshooting

### Common Recognition Issues
- **Low Confidence**: Increase image quality or adjust confidence threshold
- **False Positives**: Use more specific/cropped images
- **Not Found**: Check image path and file format
- **Variable UI**: Capture multiple variants if UI changes

### Performance Optimization
- **Optimize image sizes** for faster processing
- **Use appropriate resolution** - not too large, not too small
- **Limit the number of images** loaded at once
- **Cache frequently used images**

## Contributing Images

When contributing new images:
1. **Follow naming conventions**
2. **Ensure high quality** and consistency
3. **Test recognition** before submitting
4. **Document any special requirements**
5. **Include multiple variants** if UI changes between states

---

**Note**: The quality and accuracy of these images directly impacts the bot's performance. Take time to capture clear, consistent screenshots for best results.
