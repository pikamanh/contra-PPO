| Address | Size | Description |
|---|---:|---|
| `18` | `1` | Game Routine Index - which game routine to execute. Index in game_routine_pointer_table (bank 7 CPU address $c24d) |
| `19` | `1` | Game End Routine Index/Game Routine Init Flag - after beating the game, used to index into game_end_routine_tbl to sequence the screen fade, helicopter animation, credits, restart level 1, among other things. Also used during setup of a level to ensure routines have been completed. |
| `1a` | `1` | Frame Counter - loops from 0x00 to 0xff increments once per frame. Also known as the global timer |
| `1b` | `1` | NMI Check - set to 0x01 at start of nmi and 0x00 at end. Used to track if nmi occurred before game loop finished |
| `1c` | `1` | Demo Mode - 0x00 not in demo mode, 0x01 in demo mode |
| `1d` | `1` | Player Mode - 0x01 for 1 player, 0x07 for 2 player.  Not sure why developer just didn't use 0x22 (Player Mode) instead |
| `1f` | `1` | Demo Level End Flag - whether or not demo for the level has been completed and the new demo level should start |
| `20` | `1` | PPU Ready - 0x00 when at least 5 executions of nmi_start have happened indicating the PPU is ready |
| `21` | `1` | Graphics Buffer Offset - current write offset into CPU_GRAPHICS_BUFFER (RAM address $700, which contains pattern table tiles that are written to PPU. |
| `22` | `1` | Player Mode - 0x00 = single player, 0x01 = 2 player |
| `23` | `1` | Graphics Buffer Mode - defines format of the CPU_GRAPHICS_BUFFER. 0xff is for super-tile data, 0x00 is for text strings and palette data |
| `24` | `1` | Konami Code Status - 0x00 not entered, 0x01 entered |
| `25` | `1` | Pause State - 0x00 when not paused 0x01 when paused |
| `27` | `1` | Demo Level - the current level when in demo mode. Only ever 0x00, 0x01 or 0x02 as those are the only levels demoed |
| `28` | `1` | Intro Theme Delay - timer to prevent starting a level until the intro theme is complete (including explosion sound). |
| `29` | `1` | Game Over Delay Timer - timer after dying before showing score. Goes from 0x60 to 0x00 |
| `2a` | `2` | Delay Time - the 2-byte value of the current delay |
| `2c` | `1` | Level Routine Index - which level routine to execute. Index into level_routine_ptr_tbl (bank 7 CPU address $ce35) |
| `2d` | `1` | End Level Routine Index - index into either end_level_sequence_ptr_tbl (bank 3 CPU address $be09) or end_game_sequence_ptr_tbl (bank 4 CPU address $b949) |
| `2e` | `1` | Demo Fire Delay Timer - the number of frames to delay before player starts firing when demoing |
| `2f` | `1` | Player Weapon Strength - the damage strength of the player 1's current weapon. Based on bits 0-2 of P1 Current Weapon. Default = 0x00, M = 0x02, F = 0x01, S = 0x03, L = 0x02. Player 2's weapon doesn't affect this field. |
| `30` | `1` | Current Level - 0x00 to 0x07 represent levels 1 through 8. 0x9 is interpreted as game over sequence |
| `31` | `1` | Game Completion Count - the number of times the game has been completed (final boss defeated) |
| `32` | `1` | P1 Number Lives - 0x00 is last life, on game over stays 0x00 and P1 Game Over Status becomes 0x01 |
| `33` | `1` | P2 Number Lives - 0x00 is last life, on game over stays 0x00 and P2 Game Over Status becomes 0x01 |
| `34` | `1` | Random Number - random number (randomized between interrupts) |
| `36` | `1` | Number Palettes To Load - the number of palettes to load into CPU memory |
| `37` | `1` | Indoor Screen Cleared - whether indoor screen has had all cores destroyed (0 = not cleared, 1 = cleared, 0x80 = cleared and electric fence removed) |
| `38` | `1` | P1 Game Over Status - 0x00 not game over, 0x01 game over |
| `39` | `1` | P2 Game Over Status - 0x00 not game over, 0x01 game over or player 2 not playing (1 player game) |
| `3a` | `1` | Number Continues - the number of continues remaining |
| `3b` | `1` | Boss Defeated Flag - whether or not the level boss has been defeated (0x00 = no, 0x01 = yes).  After set to 0x01, the end level sequence logic uses this value as well using values 0x81 and 0x02. |
| `3c` | `2` | P1 Extra Life Score - the 2-byte value of the score required for the next extra life |
| `3e` | `2` | P2 Extra Life Score Low (collides with Konami Code Number Correct) |
| `3f` | `1` | Konami Code Number Correct - the number of successful inputs of the Konami code sequence 0x0a for all correct. |
| `3f` | `1` | Extra Life Score High (P2) |
| `40` | `1` | Level Location Type  - 0x00 = outdoor, 0x01 = indoor (base) 0x80 on indoor/base boss screen and indoor/base levels when players advancing to next screen |
| `41` | `1` | Level Scrolling Type - 0x00 = horizontal (and indoor/base) 0x01 = vertical |
| `42` | `2` | Level Screen Supertiles Pointer - 2-byte address to bank 2 containing which super-tiles to use for each screen of the level (level_x_supertiles_screen_ptr_table) |
| `44` | `2` | Level Supertile Data Pointer - 2-byte pointer to super-tile data, which defines pattern table tiles of the super-tiles that are used to make level blocks |
| `46` | `2` | Level Supertile Palette Data - 2-byte pointer address to the palettes used for each super-tile. Each byte describes the 4 palettes for a single super-tile |
| `48` | `1` | Level Alternate Graphics Position - how far into level (in number of screens) before loading alternate graphic data |
| `49` | `1` | Collision Code 1 Tile Index - pattern table tiles below this index (but not 0x00) are considered Collision Code 1 (floor) |
| `4a` | `1` | Collision Code 0 Tile Index - pattern table tiles >= 0x49 and less than this tile index are Collision Code 0 (empty) |
| `4b` | `1` | Collision Code 2 Tile Index - pattern table tiles >= $4a and less than this tile index are Collision Code 2 (water) |
| `4c` | `4` | Level Palette Cycle Indexes - palette indexes into game_palettes (bank 7 CPU address $d227) to cycle through for the level for the 4th nametable palette index |
| `50` | `8` | Level Palette Index - the level's initial background palettes [$50 to $54) and sprite palettes [$54 to $58). Offsets into game_palettes (bank 7 CPU address $d227). |
| `58` | `1` | Level Stop Scroll - the screen of the level to stop scrolling. Set to 0xff when boss auto scroll starts |
| `59` | `1` | Level Solid Background Collision Check - used to determine whether to check for bullet and weapon item solid bg collisions When non-zero, specifies weapon item should check for solid bg collisions.  When negative, used to let bullet (player and enemy) collision detection code to know to look for bullet-solid background collisions. |
| `5a` | `1` | P1 Demo Input Number of Frames - how many even-numbered frames to continue pressing the button specified in Demo Input Value ($5c) for demo |
| `5b` | `1` | P2 Demo Input Number of Frames |
| `5c` | `1` | P1 Demo Input Value - the current controller input pressed during demo |
| `5d` | `1` | P2 Demo Input Value |
| `5e` | `1` | P1 Demo Input Table Index - when in demo, stores the offset into specific demo_input_tbl_lX_pX (bank 5) |
| `5f` | `1` | P2 Demo Input Table Index |
| `60` | `1` | PPU Write Tile Offset - the current write offset of the super-tile data, number of tiles outside the current view. Horizontal levels loops from 0x00 to 0x1f. Vertical starts with 0x1d goes down to 0x00 before looping. |
| `61` | `1` | Level Transition Timer - used in vertical levels to time animation between sections for every 'up' input. Also used in indoor levels between screens to animate moving forward. |
| `62` | `2` | PPU Write Address- 2-byte PPU write address to CPU Graphics Buffer ($700) |
| `64` | `1` | Level Screen Number - the screen number of the current level, i.e. how many screens into the level |
| `65` | `1` | Level Screen Scroll Offset - the number of pixels into Level Screen Number the level has scrolled. Goes from 0x00-0xff for each screen (256 pixels) |
| `66` | `2` | Attribute Table Write Address - the 2-byte attribute table write address |
| `68` | `1` | Frame Scroll - how much to scroll the screen this frame based on player velocity (usually 0x00 or 0x01). For vertical levels, up to 0x04 |
| `69` | `1` | Supertile Nametable Offset - base nametable offset into memory address into CPU graphics buffer starting at Level Screen Supertiles ($0600). Always either 0x00 (nametable 0) or 0x40 (nametable 1), points to area that contains the super-tile indexes for screen |
| `6a` | `1` | Sprite Load Type - which sprites to load 0x00 = normal sprites, 0x01 = Heads Up Display (HUD) sprites |
| `6b` | `1` | Continue End Selection - 0x00 = "CONTINUE" is selected 0x01 = "END" is selected. Used in game over screen |
| `71` | `1` | Alternate Graphic Data Loading Flag 0x00 = alternate graphics data should not be loaded 0x01 = alternate graphics data should be loaded 0x02 = alternate graphics data are currently being loaded |
| `72` | `1` | Level Palette Cycle - the current iteration of the palette animation loop. 0x00 up to entry for level in lvl_palette_animation_count (bank 7 CPU address $d181) |
| `73` | `1` | Indoor Scroll - scrolling on indoor level changes 0x00 = not scrolling; 0x01 = scrolling, 0x02 = finished |
| `74` | `1` | Background Palette Adjust Timer - timer used for adjusting background palette colors (not sprite palettes). Used for fade-in effect of dragon and boss UFO as well as indoor transitions |
| `75` | `1` | Auto Scroll Timer 0 - used when completing scroll to show a boss, e.g. vertical level dragon screen |
| `76` | `1` | Auto Scroll Timer 1 - used when completing scroll to show a boss, e.g. alien guardian |
| `77` | `1` | Tank Auto Scroll - amount to scroll every frame for snow field tanks (dogras), regardless of Auto Scroll Timer 0 and 1 |
| `78` | `1` | Pause Palette Cycle - 0x00 = nametable palettes 0x03 and 0x04 will cycle through colors like normal.  Non-zero values will pause palette color cycling. |
| `79` | `1` | Soldier Generation Routine - which routine is currently in use for generating soldiers. Index into soldier_generation_ptr_tbl (bank 2 CPU address $b537) |
| `7a` | `1` | Soldier Generation Timer - a timer between soldier generation. 0x00 = no generation. |
| `7b` | `1` | Soldier Generation X Position - the initial x position of the generated soldier |
| `7c` | `1` | Soldier Generation Y Position - the initial y position of the generated soldier |
| `7d` | `1` | Falcon Flash Timer - the number of frames to flash the screen for falcon weapon item |
| `7f` | `1` | Tank Ice Join Scroll Flag - whether or not to have the ice joint enemy move left while player walks right to simulate being on the background. (snow field level) |
| `80` | `2` | Enemy Level Routines - 2-byte address to the correct enemy_routine_level_XX (bank 7) for the current level, used to retrieve enemy routines for the level-specific enemies |
| `82` | `1` | Enemy Screen Read Offset - read offset into level_xx_enemy_screen_xx (bank 2) table, which specifies the enemies on each screen of a level |
| `83` | `1` | Enemy Current Slot - specifies the current enemy slot that is being executed |
| `84` | `1` | Boss Auto Scroll Complete - set when boss reveal auto-scrolling has completed |
| `85` | `1` | Boss Screen Enemies Destroyed - used on level 3 and level 7 boss screens to keep track of how many dragon arm orbs or mortar launchers have been destroyed respectively |
| `86` | `1` | Wall Core Remaining - remaining wall cores/wall platings to destroy until can advance to next screen. For level 4 boss, used to count remaining boss gemini |
| `87` | `1` | Wall Plating Destroyed Count - used in indoor/base boss levels to keep track of how many wall platings (ENEMY_TYPE 0x0a) have been destroyed |
| `88` | `1` | Indoor Enemy Attack Count - used in indoor/base levels to specify how many 'rounds' of attack have happened per screen, max 0x07 before certain enemies no longer generate. Indoor soldiers, jumping soldiers, indoor rollers, and wall core check this value |
| `89` | `1` | Indoor Red Soldier Created - used in indoor/base levels to indicate if a red jumping soldier has been created, to prevent creation of another |
| `8a` | `1` | Grenade Launcher Flag - used in indoor/base levels to indicate that a grenade launcher enemy (ENEMY_TYPE 0x17) is on the screen. Prevents other indoor enemies from being generated |
| `8b` | `1` | Alien Fetus Aim Timer Index - used to keep track of the index into alien_fetus_aim_timer_tbl (bank 0 CPU address $b7e8) to set the delay between re-aiming towards the player |
| `8e` | `1` | Enemy Attack Flag - whether or not enemies will fire at player, also whether or not random enemies are generated, bosses ignore this value |
| `90` | `1` | P1 Player State - 0x00 falling into level, 0x01 normal state, 0x02 when dead, 0x03 can't move |
| `91` | `1` | P2 Player State - same as P1 Player State.  If p2 not playing, set to 0x00 |
| `92` | `1` | P1 Indoor Transition X Accumulator - used to help calculate fractional x velocity when moving between screens on indoor/base levels |
| `93` | `1` | P2 Indoor Transition X Accumulator |
| `94` | `1` | P1 Player Jump Coefficient - used to keep track of fractional y velocity on vertical levels for overflowing fractional velocity. Also used to help calculate fractional y velocity when moving between screens on indoor/base levels. |
| `95` | `1` | P2 Player Jump Coefficient |
| `96` | `1` | P1 Indoor Transition X Fractional Velocity - indoor animation transition when walking into screen x fractional velocity |
| `97` | `1` | P2 Indoor Transition X Fractional Velocity |
| `98` | `1` | P1 Player X Velocity - the player's x velocity (0x00, 0x01, or 0xff) |
| `99` | `1` | P2 Player X Velocity |
| `9a` | `1` | P1 Indoor Transition Y Fractional Velocity - indoor animation transition when walking into screen y fractional velocity |
| `9b` | `1` | P2 Indoor Transition Y Fractional Velocity |
| `9c` | `1` | P1 Indoor Transition Y Fast Velocity - indoor animation transition when walking into screen y fast velocity |
| `9d` | `1` | P2 Indoor Transition Y Fast Velocity |
| `9e` | `1` | P1 Player Animation Frame Timer - value that is incremented every frame when player is walking. Used to wait 0x08 frames before incrementing Player Animation Frame Index ($a6) for animating player walking |
| `9f` | `1` | P2 Player Animation Frame Timer |
| `a0` | `1` | P1 Player Jump Status - the status of the player jump. Similar to Edge Fall Code ($a4) * high nibble is for facing direction * bit 7 - set when jumping left * low nibble is 0x01 when jumping, 0x00 when not |
| `a1` | `1` | P2 Player Jump Status |
| `a2` | `1` | P1 Player Frame Scroll - how much player is causing the frame to scroll by, see Frame Scroll ($68) |
| `a3` | `1` | P2 Player Frame Scroll |
| `a4` | `1` | P1 Edge Fall Code - similar to Player Jump Status ($a0). Used to initiate gravity pulling player down * if bit 7 set, then falling through platform * if bit 6 is set, then walking left off edge * if bit 5 is set, then walking right off ledge |
| `a5` | `1` | P2 Edge Fall Code |
| `a6` | `1` | P1 Player Animation Frame Index - which frame of the player animation. Depends on player state. For example, if player is running, this cycles from 0x00 to 0x05. |
| `a7` | `1` | P2 Player Animation Frame Index |
| `a8` | `1` | P1 Player Indoor Animation Y - the y position the player was at when they started walking into screen after clearing an indoor level. I believe it's always 0xa8 since y position is hard-coded for indoor levels |
| `a9` | `1` | P2 Player Indoor Animation Y |
| `aa` | `1` | P1 Current Weapon - low nibble is what weapon P1 has, high nibble 1 is rapid fire flag, commonly abbreviated MFSL 0x00 - Regular, 0x01 - Machine Gun, 0x02 - Flame Thrower 0x03 - Spray, 0x04 - Laser, bit 4 set for rapid fire |
| `ab` | `1` | P2 Current Weapon |
| `ac` | `1` | P1 Player M Weapon Fire Time - used when holding down the B button with the m weapon.  High nibble is number of bullets generated (up to 0x06), low nibble is counter before next bullet is generated (up to 0x07) |
| `ad` | `1` | P2 Player M Weapon Fire Time |
| `ae` | `1` | P1 New Life Invincibility Timer - timer for invincibility after dying |
| `af` | `1` | P2 New Life Invincibility Timer |
| `b0` | `1` | P1 Invincibility Timer - timer for player invincibility (b weapon). Decreases every 8 frames., usually set to 0x80 except level 7 when set to 0x90. |
| `b1` | `1` | P2 Invincibility Timer |
| `b2` | `1` | P1 Player Water State * bit 1 - horizontal sprite flip flag * bit 2 - set when player in water, or exiting water * bit 3 - player is walking out of water * bit 4 - finished initialization for entering water * bit 7 - player is walking out of water |
| `b3` | `1` | P2 Player Water State |
| `b4` | `1` | P1 Player Death Flag - bit 0 specifies whether player has died, bit 1 specifies player was facing left when hit, used so player dies lying in appropriate direction |
| `b5` | `1` | P2 Player Death Flag |
| `b6` | `1` | P1 Player On Enemy - whether or not the player is on top of another enemy (0x14 - mining cart, 0x15 - stationary mining cart, 0x10 - floating rock platform) |
| `b7` | `1` | P2 Player On Enemy |
| `b8` | `1` | P1 Player Fall X Freeze - used to prevent changing X velocity shortly after walking off/falling through ledge, set to Y post of ledge + 0x14 |
| `b9` | `1` | P2 Player Fall X Freeze |
| `ba` | `1` | P1 Player Hidden - 0x00 player visible, 0x01/0xff player invisible (any non-zero). I believe it is meant to track distance off screen the player is |
| `bb` | `1` | P2 Player Hidden |
| `bc` | `1` | P1 Player Sprite Sequence - which animation to show for the player * outdoor - 0x00 standing (no animation), 0x01 gun pointing up, 0x02 crouching, 0x03 walking or curled jump animation, 0x04 dead animation * indoor - 0x00 standing facing back wall, 0x01 electrocuted, 0x02 crouching, 0x03 walking left/right animation, 0x05 walking into screen (advancing), 0x06 dead animation |
| `bd` | `1` | P2 Player Sprite Sequence |
| `be` | `1` | P1 Player Indoor Animation X - the x position the player was at when they started walking into screen after clearing an indoor level |
| `bf` | `1` | P2 Player Indoor Animation X |
| `c0` | `1` | P1 Player Aim Previous Frame - backup of Player Aim Direction ($c2) |
| `c1` | `1` | P2 Player Aim Previous Frame - backup of Player Aim Direction ($c3) |
| `c2` | `1` | P1 Player Aim Direction - which direction the player is aiming [0x00-0x0a] depends on level and jump status (00 up facing right, 1 up-right, 2 right, 3 right-down, 4 crouching facing right, 5 crouching facing left, etc).  There are 0x02 up and 0x02 down values depending on facing direction. |
| `c3` | `1` | P2 Player Aim Direction |
| `c4` | `1` | P1 Player Y Fractional Velocity - the fractional portion of the player's y velocity |
| `c5` | `1` | P2 Player Y Fractional Velocity |
| `c6` | `1` | P1 Player Y Fast Velocity - the integer portion of the player's y velocity. Positive pulls down, negative pulls up |
| `c7` | `1` | P2 Player Y Fast Velocity |
| `c8` | `1` | P1 Electric Shock Timer - timer for player being shocked, used to freeze player and modify look after touching electricity |
| `c9` | `1` | P2 Electric Shock Timer |
| `ca` | `1` | P1 Indoor Player Jump Flag - used when entering new screen to tell the engine to cause the player to jump |
| `cb` | `1` | P2 Indoor Player Jump Flag |
| `cc` | `1` | P1 Player Water Timer - timer used for getting into and out of water |
| `cd` | `1` | P2 Player Water Timer |
| `ce` | `1` | P1 Player Recoil Timer - how many frames to be pushed back/down from recoil |
| `cf` | `1` | P2 Player Recoil Timer |
| `d0` | `1` | P1 Indoor Player Advance Flag - whether or not the player is walking into screen when advancing between screens on indoor levels, used for animating player |
| `d1` | `1` | P2 Indoor Player Advance Flag |
| `d2` | `1` | P1 Player Special Sprite Timer - used to track animation for player death animation.  For outdoor levels, it is a timer that increments once player hit, every 0x08 frames updates to next animation frame until 0x04.  Also used to track jumping curl animation (loops from 0x00-0x04) |
| `d3` | `1` | P2 Player Special Sprite Timer |
| `d4` | `1` | P1 Player Fast X Velocity Boost - the x fast velocity boost from landing on a non-dangerous enemy, e.g. moving cart or floating rock in vertical level |
| `d5` | `1` | P2 Player Fast X Velocity Boost |
| `d6` | `1` | P1 Player Sprite Code - sprite code of the player |
| `d7` | `1` | P2 Player Sprite Code - sprite code of the player |
| `d8` | `1` | P1 Player Sprite Flip - stores player sprite horizontal (bit 6) and vertical (bit 7) flip flags before saving into SPRITE_ATTR. Bit 3 specifies whether the Player Animation Frame Index ($a6) is even or odd |
| `d9` | `1` | P2 Player Sprite Flip |
| `da` | `1` | P1 Player Background Flag and Edge Detect * bit 7 specifies the player's sprite attribute for background priority. Allows player to walk behind opaque background (OAM byte 2 bit 5).  0x00 = sprite in foreground, 0x01 = sprite is background * bit 0 allows the player to keep walking horizontally off a ledge without falling |
| `db` | `1` | P2 Player Background Flag and Edge Detect |
| `df` | `1` | Game Over Bit Field - combination of both players game over status. * 0x00 = p1 not game over, p2 game over (or not playing) * 0x01 = p1 game over, p2 not game over * 0x02 = p1 nor p2 are in game over |
| `ec` | `2` | Sound Table Pointer - 2-byte address pointing of index into sound_table_00 （bank 1 CPU address $88e8) |
| `f1` | `1` | P1 Controller State - stores the currently-pressed buttons * bit 7 - A * bit 6 - B * bit 5 - select * bit 4 - start * bit 3 - up * bit 2 - down * bit 1 - left * bit 0 - right |
| `f2` | `1` | P2 Controller State |
| `f5` | `1` | P1 Controller State Diff - stores the difference between the controller input between reads. Useful for events that should only trigger on first button press |
| `f6` | `1` | P2 Controller State Diff |
| `f9` | `1` | P1 Controller Known Good - used in input-reading code to know the last known valid read of controller input (similar to P1 Controller State ($f1) |
| `fa` | `1` | P2 Controller Known Good |
| `fc` | `1` | Vertical Scroll - the number of pixels to vertically scroll down. * horizontal levels are always 0xe0 (224 pixels or 28 tiles down) * indoor/base are always 0xe8 (232 or 29 tiles down) * waterfall level (vertical level) starts at 0x00 and decrements as players move up screen (wrapping) |
| `fd` | `1` | Horizontal Scroll - the horizontal scroll component of the PPUSCROLL, [0x00 - 0xff] |
| `fe` | `1` | PPU Mask Settings - used to store value of PPUMASK before writing to PPU |
| `ff` | `1` | PPU Control Settings - used to set PPUCTRL value for next frame |
| `100` | `6` | Sound Command Length - how many video frames the sound count should last for, i.e. the time to wait before reading next sound command.  One for each of the 0x06 sound slots. |
| `106` | `6` | Sound Code - the sound code for each of the 0x06 sound slots |
| `10c` | `6` | Sound Pulse Length - APU_PULSE_LENGTH for each of the 0x06 sound slots |
| `112` | `6` | Sound Command Adress Low Byte - low byte of address to current sound command.  0x06 slots, one for each sound slot |
| `118` | `6` | Sound Command Address High Byte - high byte of address to current sound command. 0x06 slots, one for each sound slot |
| `11e` | `2` | Sound Volume Envelope - pulse channel volume.  Either an offset into pulse_volume_ptr_tbl (bank 1 CPU address $8001) which specifies the volume for the frame or a specific volume to use. When bit 7 is set, then the volume will auto decrescendo. |
| `120` | `1` | Sound Current Slot - the current sound slot 0x00-0x05 inclusively. |
| `121` | `1` | Percussion Index Backup - backup location for percussion_tbl (bank 1 CPU address $82 cd) index to restore after call to play_sound (bank 7 CPU address $c16b) |
| `122` | `1` | Initial Sound Code - the sound code to load. Sound codes greater than 0x5a are dmc sounds |
| `123` | `1` | Sound Channel Register Offset - 0x00 for first pulse channel, 0x04 for second, 0x08 for triangle, 0x0c for noise |
| `124` | `1` | Sound Flags - sound channel flags * bit 0 - 0 = sound effect, 1 = music * bit 1 - 1 = decrescendo end pause complete, resume decrescendo, 0 = keep volume constant * bit 2 - 0 = use lvl_config_pulse (bank 1 CPU address $8154) to set volume for frame, 1 = automatic decrescendo logic * bit 3 - signifies that a shared (child) sound command is executing. Used to know, after finishing parsing a sound command, whether or not to done or should return to parent sound command * bit 4 - slightly flatten note * bit 5 - 1 = decrescendo should be paused for a duration * bit 6 - mute flag (1 = muted, 0 = not muted) * bit 7 - sweep flag |
| `12a` | `1` | Level Pulse Volume Index - index into level pulse volume table |
| `12a` | `1` | Pulse Volume Duration - the number of video frames to decrement the volume for, before stopping decrescendo and keeping final volume |
| `12f` | `1` | Pause State 1 - whether or not the game is paused, used for sound logic (see Pause State ($25)) |
| `130` | `1` | Pulse Channel 1 Decrescendo End Pause - number of video frames before end of sound command in which the decrescendo will resume |
| `131` | `1` | Pulse Channel 2 Decrescendo End Pause |
| `132` | `4` | Sound Pitch Adjust - the amount added to the sound byte low nibble before loading the correct note period value |
| `136` | `6` | Sound Command Multiplier - amount to multiply to when calculating when to stop decrescendo |
| `13c` | `6` | Sound Volume Adjust - used to adjust volume amount when setting volume |
| `142` | `1` | Sound Slot 0 Config Low - the value to merge with the high nibble before storing in APU channel config register for pulse channel |
| `143` | `1` | Sound Slot 1 Config Low |
| `144` | `1` | Sound Triangle Config - in memory value for the triangle channel configuration. |
| `148` | `6` | Sound Repeat Count - used for 0xfe sound commands to specify how many times to repeat a shared sound part |
| `14e` | `1` | Pulse Channel 1 Sound Config High - the value to merge with the volume when saving the pulse config |
| `14f` | `1` | Pulse Channel 2 Sound Config High |
| `152` | `1` | Pulse Channel 1 Sound Config High - Sound Slot 0x04 |
| `154` | `6` | Sound Length Multiplier - value used when determining how many video frames to wait before reading next sound command. |
| `15a` | `6` | Sound Period Rotate - when not 0x04, the number of times to shift the high byte of note period index into the low byte |
| `160` | `6` | Pulse Volume - low nibble only, stores the volume for the pulse channels |
| `166` | `6` | New Sound Code Low Address - sound command return location low byte once sound command specified executes |
| `16c` | `6` | New Sound Code High Address - sound command return location high byte once sound command specified executes |
| `172` | `6` | Sound Pulse Period - APU Pulse Period value |
| `178` | `1` | Sound Slot 0 Vibrato Control - [0x00-0x03], 0x80 = no vibrato. Even values cause the note to stay the same, odd values cause vibrato 0x03 = pitch up, 0x01 = pitch down |
| `179` | `1` | Sound Slot 1 Vibrato Control |
| `17a` | `1` | Sound Slot 0 Volume Timer - sound command counter; increments up to Vibrato Delay ($17e), at which vibrato will be checked, only increments when Vibrato Control ($178) is non-negative, i.e. not 0x80 |
| `17b` | `1` | Sound Slot 1 Volume Timer |
| `17c` | `1` | Sound Slot 0 Note - the pulse channel note that is sustained or has the vibrato applied to for pulse channels (in Contra only ever sustained no vibrato) |
| `17d` | `1` | Sound Slot 1 Note |
| `17e` | `1` | Sound Slot 0 Pulse Vibrato Delay - used to delay start of vibrato until Sound Volume Timer ($17a) has counted up to this value. If a note isn't as long as the delay, then vibrato won't be considered for a note |
| `17f` | `1` | Sound Slot 1 Pulse Vibrato Delay |
| `180` | `1` | Sound Slot 0 Vibrato Amount - the amount of vibrato to apply |
| `181` | `1` | Sound Slot 1 Vibrato Amount - the amount of vibrato to apply |
| `190` | `1` | Level End Delay Timer - a delay timer before beginning level end animation sequence |
| `191` | `1` | Level End Sequence 1 Timer - a delay timer specifying the duration of end_level_sequence_01 (bank 3 CPU address $be3c). Decremented every other frame |
| `192` | `1` | P1 Level End Level Routine State - used by level end routines for managing animation state. For example, indoor level end animations have 4 states: walk to elevator, initialize elevator sprite, ride elevator |
| `193` | `1` | P2 Level End Level Routine State - used by level end routines |
| `194` | `1` | Level End Players Alive - the number of players alive at the end of the level, used to know if should play level end music |
| `195` | `1` | Soldier Generation Screen - the current screen that soldiers are being generated for |
| `196` | `1` | Screen Generation Soldiers - the total number of soldiers that have been generated for the current screen |
| `200` | `100` | OAM DMA CPU Buffer - OAMDMA (sprite) data, read once per frame |
| `300` | `a` | Player Sprites - player sprites, p1 and p2 sprite, then player bullets |
| `30a` | `10` | Enemy Sprites - enemy sprites to load on screen |
| `31a` | `a` | Player Sprite Y Positions - y position on screen of each player sprite. |
| `324` | `10` | Enemy Y Positions - y position on screen of each enemy sprite |
| `334` | `10` | Player Sprite X Positions - x position of screen of each player sprite and player bullets |
| `33e` | `10` | Enemy X Positions - x position on screen of each enemy sprite |
| `34e` | `a` | Player Sprite Attributes - sprite attribute, specifies palette, vertical flip, horizontal flip, and whether to adjust y position * bit 0 and 1 - sprite palette * bit 2 - 0 to use default palette from sprite code *       - 1 to use palette specified in bits 0 and 1 * bit 3 - whether to add 0x01 to sprite y position, used for recoil effect firing weapon * bit 5 - bg priority * bit 6 - whether to flip the sprite horizontally * bit 7 - whether to flip the sprite vertically |
| `358` | `10` | Enemy Sprites Attributes - enemy sprite attribute. See specification above for Player Sprite Attributes |
| `368` | `10` | Player Bullet Sprite Code - the sprite codes to load for the bullet |
| `378` | `10` | Player Bullet Sprite Attribute - the sprite attributes for the bullet (see Player Sprite Attributes ($34e) for specification) Used for L bullets for flipping the angled sprites depending on direction |
| `388` | `10` | Player Bullet Slot - 0x00 when no bullet, otherwise stores bullet type + 1, i.e. 0x01 basic, 0x02 M, 0x03 F bullet, 0x04 S,0x05 L, can be negative sometimes |
| `398` | `10` | Player Bullet Velocity Y Accumulator - an accumulator to keep track of Player Bullet Y Velocity Fractional ($3f8) being added to itself have elapsed before adding 1 to Player Bullet Y Position ($3b8) |
| `3a8` | `10` | Player Bullet Velocity X Accumulator - an accumulator to keep track of Player Bullet X Velocity Fractional ($3e8) being added to itself have elapsed before adding 1 to Player Bullet X Position ($3c8) |
| `3b8` | `10` | Player Bullet Y Position - the bullet's sprite y position |
| `3c8` | `10` | Player Bullet X Position - the bullet's sprite x position.  For F bullets, Player Bullet FS X ($478) and this value together determine x position |
| `3d8` | `10` | Player Bullet Y Velocity Fractional - percentage out of 0-255 set number of frames until Y position is incremented by an additional 1 unit |
| `3e8` | `10` | Player Bullet X Velocity Fractional - percentage out of 0-255 set number of frames until X position is incremented by an additional 1 unit |
| `3f8` | `10` | Player Bullet Y Velocity Fast - player bullet velocity y integer part |
| `408` | `10` | Player Bullet X Velocity Fast - player bullet velocity x integer part |
| `418` | `10` | Player Bullet Timer - 'timer' starts at 0x00. Used by F, S (indoor only) and L * for indoor S, used to specify size of bullet * For F, used to set x and y pos when traveling to create swirl. Increments or decrements every frame depending on firing direction (left decrement, right increment) * For L used to spread out 4 lasers for one shot |
| `428` | `10` | Player Bullet Aim Direction - the direction of the bullet 0x00 for up facing right, incrementing clockwise up to #09 for up facing left |
| `438` | `10` | Player Bullet Routine - 0x00, 0x01, or 0x03 |
| `448` | `10` | Player Bullet Owner - 0x00 player 1 bullet, 0x01 player 2 bullet |
| `458` | `10` | Player Bullet F Rapid - 0x01 for player indoor bullets for F weapon when rapid fire is enabled |
| `458` | `10` | Player Bullet S Indoor Adjust - for indoor S bullets, specifies whether to adjust Player bullet X Position ($3c8) by an additional -1 (0xff) every frame |
| `468` | `10` | Player Bullet Distance - represents how far a bullet has traveled * for S outdoor bullets, used to determine the size (scale) of the bullet * for F on indoor levels, used to determine spiraling position based on distance from player |
| `468` | `10` | Player Bullet S Adjust Accumulator - for indoor S weapons, stores accumulated fractional velocity where overflow affects Player Bullet S Indoor Adjust ($458) |
| `478` | `10` | Player Bullet FS X - used to offset from general x direction of bullet for swirl effect in F bullet and spread effect in S bullet (indoor). Specifies center x position on screen f bullet swirls around. Used when firing f bullet either left, right, or at an angle |
| `488` | `10` | Player Bullet F Y - center y position on screen f bullet swirls around. Used when firing f bullet either up, down, or at an angle. |
| `488` | `10` | Player Bullet S Rapid - for S weapon in indoor levels, specifies whether weapon is rapid fire or not |
| `498` | `10` | Player Bullet Velocity FS X Accumulator - an accumulator to keep track of Player Bullet X Velocity Fractional ($3e8) being added to itself have elapsed before adding 1 to Player Bullet X Position ($3c8) |
| `4a8` | `10` | Player Bullet Velocity F Y Accumulator - (for F weapon only) an accumulator to keep track of Player Bullet Y Velocity Fractional ($3d8) being added to itself have elapsed before adding 1 to Player Bullet Y Position ($3b8) |
| `4a8` | `10` | Player Bullet S Bullet Number - for S weapon only, specifies the number the bullet in the current 'spray' for the shot. Per shot of S weapon, 0x05 bullets are generated. If no other bullets exist then $04a8 would have 0x00, $04a9 would have 0x01 $04a9 would have 0x02, etc. |
| `4b8` | `10` | Enemy Routine - enemy routine indexes. Subtract 1 to get real routine, since all offsets are off by 1 |
| `4c8` | `10` | Enemy Y Velocity Accumulator - an accumulator to keep track of Enemy Y Velocity Fractional ($4f8) being added to itself have elapsed before adding 1 to Enemy Y Position ($324) |
| `4d8` | `10` | Enemy X Velocity Accumulator - an accumulator to keep track of Enemy X Velocity Fractional ($518) being added to itself have elapsed before adding 1 to Enemy X Position ($33e) |
| `4e8` | `10` | Enemy Y Velocity Fast - the number of units to add to Enemy Y Position ($324) every frame |
| `4f8` | `10` | Enemy Y Velocity Fractional - percentage out of 0-255 of a unit to add, e.g. if 0x80 (0x80/0xff = 50%), then every other frame will cause Y position to increment by 1 |
| `508` | `10` | Enemy X Velocity Fast - the number of units to add to Enemy X Position ($33e) every frame |
| `518` | `10` | Enemy X Velocity Fractional - percentage out of 0-255 of a unit to add, e.g. if 0x80 (0x80/0xff = 50%), then every other frame will cause X position to increment by 1 |
| `528` | `10` | Enemy Type - enemy type, e.g. 0x03 = flying capsule |
| `538` | `10` | Enemy Animation Delay - used for various delays by enemy logic |
| `548` | `10` | Enemy Variable A - variable used for various purposes by some enemy types, e.g. the sound code to play when enemy hit by player bullet. Dragon arm orb uses it for adjusting enemy position, fire beam uses it for animation delay |
| `558` | `10` | Enemy Attack Delay - the delay before an enemy attacks, for weapon items and grenades this is used for helping calculate falling arc trajectory instead of enemy delay |
| `558` | `10` | Enemy Variable B - for weapon items and grenades this is used for helping calculate falling arc trajectory instead of enemy delay |
| `568` | `10` | Enemy Frame - animation frame the enemy is in, typically indexes into an enemy type-specific table of sprite codes |
| `588` | `10` | Enemy Score Collision - represents 3 things for an enemy * SSSS CCCC - score code and collision type * also explosion type |
| `578` | `10` | Enemy HP - typically the HP of the enemy |
| `598` | `10` | Enemy State Width - various properties * bit 7 set to allow bullets to travel through enemy, e.g. weapon item * bit 6 specifies whether player can land on enemy (floating rock and moving cart), bit 4 also has to be 0 * bit 4 and 5 specify the collision box type * bit 3 determines the explosion type * bit 2 for bullets specifies whether to play sound on collision * bit 1 specifies whether to play explosion noise; also specifies width of enemy * bit 0 - 0x00 test player-enemy collision, 0x01 means to skip player-enemy collision test |
| `5a8` | `10` | Enemy Attributes - enemy type-specific attributes that define how an enemy behaves and/or looks |
| `5b8` | `10` | Enemy Variable 1 - a byte available to each enemy for whatever they want to use it for |
| `5c8` | `10` | Enemy Variable 2 - a byte available to each enemy for whatever they want to use it for |
| `5d8` | `10` | Enemy Variable 3 - a byte available to each enemy for whatever they want to use it for |
| `5e8` | `10` | Enemy Variable 4 - a byte available to each enemy for whatever they want to use it for |
| `600` | `80` | Level Screen Supertiles - CPU  memory address where super tiles indexes for the screens of the level are loaded. 2 screens are stored in the CPU buffer.  The second screen loaded at $0640. |
| `680` | `20` | Background Collision Data - map of collision types for each of the super-tiles for both nametables, each 2 bits encode 1/4 of a super-tile's collision information. First 8 nibbles are a row of the top of super-tile, the next 8 are the middle middle. Not used on base (indoor) levels |
| `700` | `50` | CPU Graphics Buffer - used to store data that will be then moved to the PPU. repeating structure * byte 0 is multifaceted * if 0x0, then done writing graphics buffer to PPU * if greater than 0x0, then there is data to write, this byte is the offset into vram_address_increment * both 0x01, and 0x03 signify VRAM address increment to 0, meaning to add 0x1 every write to PPU (write across) * 0x02 signifies VRAM address increment is 1, meaning add 0x20 (32 in decimal) every write to PPU (write down) * if Graphics Buffer Mode ($23) is 0xff then * byte 1 is length of the tiles being written per group * byte 2 is the number of $701-sized blocks to write to the PPU * for each block, the block prefixed with 2 bytes specifying PPU address (high byte, then low byte) * if Graphics Buffer Mode ($23) is 0x00 * if byte 0x00 is 0x00, then no drawing takes place for frame * blocks of text/palette data prefixed with 2 bytes specifying PPU address (high byte, then low byte). the block of text is ended with a 0xff, if the byte after 0xff is the vram_address_increment offset. then the the process continues, i.e. read 0x02 PPU address bytes, read next text |
| `7c0` | `20` | Palette CPU Buffer - the CPU memory address of the palettes eventually loaded into the PPU $3f00 to $3f1f |
| `7e0` | `2` | High Score - the 2-byte high score |
| `7e2` | `2` | Player 1 Score - the 2-byte score for player 1 |
| `7e4` | `2` | Player 2 Score - the 2-byte score for player 2 |
| `7ec` | `1` | Previous ROM Bank - the previously-loaded PRG BANK |
| `7ed` | `1` | Previous ROM Bank 1 - the previously-loaded PRG BANK, but used only when playing sounds, otherwise a duplicate use of Previous ROM Bank ($7ec) |
