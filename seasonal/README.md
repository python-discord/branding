### Seasonal branding

Each folder in this directory contains branding inspired by a specific season. Such assets are temporarily applied to the server to celebrate holidays, promote on-going events, or to show support for various world-wide movements.

While the primary function is to organize the various assets we have, they are also used by **Seasonalbot's branding manager**. The bot will automatically apply seasonal assets pulled directly from this repository to the server. In order for Seasonalbot to properly detect and apply assets, certain conventions must be followed.

#### Automatically managed assets

There are 3 types of seasonal assets: **server icons**, **server banners**, and **bot avatars**. While a season always has **at most 1** banner and bot avatar, there may be **multiple** server icons. In such a case, Seasonalbot will periodically cycle available icons at a configurable interval (once every *n* days).

In order for banners and avatars to be discovered, they shall be placed directly in a seasonal directory, named `seasonal/<season_name>/banner.png` and `.../avatar.png` respectively. Note that these assets are expected to *always* carry the **png** extension. Server icons shall always (regardless of whether the is only 1, or many) be placed in a nested directory, as follows: `.../server_icons/festive_256.gif`. Server icons are name and extension agnostic - they are registered simply by being present in the `server_icons/` directory.

If a non-evergreen season does not provide all assets, the bot will search for the missing ones in the evergreen directory. We will illustrate this behaviour with the following example:

```
├── seasonal/
│
│ ├── easter/
│ │ ├── avatar.png
│ │ ├── banner.png
│
│ ├── christmas/
│ │ ├── server_icons/
│ │ │ ├── snowing.gif
│ │ ├── avatar.png
│
│ ├── evergreen/
│ │ ├── server_icons/
│ │ │ ├── winky.gif
│ │ │ ├── spinner.png
│ │ ├── avatar.png
│ │ ├── banner.png
```

While the **easter** season is active, the bot will apply its `avatar.png` and `banner.png` assets. However as the season does not provide any server icons, the bot will continue to cycle the evergreen ones - `winky.gif` and `spinner.png`.

Once we enter the **christmas** season, the bot will apply the `snowing.gif` server icon - it will not cycle, as there is only one icon. Additionally, the christmas `avatar.png` will be used. However, the bot will fall back to the evergreen `banner.png`.

While no specific season is active, the bot simply uses the evergreen one.

This means that there will **always** be available assets, as long as they are present in the evergreen directory. Should an asset become missing in this directory, the bot will simply ignore it.

Failure to comply with this schema will not break Seasonalbot, but it will prevent its branding manager from functioning properly. Please refer to its `BrandingManager` cog for further documentation and implementation details.

#### Other assets

Any files or sub-directories *not* listed above will be entirely ignored by Seasonalbot. A seasonal directory may be arbitrarily structured, as long as it doesn't interfere with the above-described conventions. This includes the `server_icons/` directory, which can have an arbitrary amount of sub-directories that the bot will ignore. Seasonalbot will *only* cycle **files** *directly* in `server_icons/`.

For example:

```
│ ├── some_season/
│ │ ├── server_icons/
│ │ │ ├── alt_size/
│ │ │ │ ├── a_large.gif
│ │ │ │ ├── b_large.png
│ │ │ ├── a.gif
│ │ │ ├── b.png
│ │ ├── avatar.png
│ │ ├── banner.png
│ │ ├── random_cat_pic.png
```

In such a case, the bot will cycle `a.gif` and `b.png` server icons, and use the provided `avatar.png` and `banner.png`. All other files are ignored.
