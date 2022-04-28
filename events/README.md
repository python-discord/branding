# Events

This directory contains branding for events celebrated by Python Discord. Events are automatically discovered by the [Python](https://github.com/python-discord/bot/) bot and have their assets applied to the Discord guild when active. As such, event directories must follow a specific structure.

## Event directory structure

For an event directory to be valid, it has to contain the following assets.

### `meta.md`

Meta files consist of two sections: a [YAML frontmatter](https://assemble.io/docs/YAML-front-matter.html) with the event's metadata, and a Markdown description.

In the frontmatter of each such file, each event must either be registered as the fallback:

```yaml
fallback: true
```

Or have a specified period:

```yaml
start_date: July 10
end_date: July 20
```

There must be exactly 1 fallback event, and 0 or more non-fallback events. Events cannot collide in time, and the end date must either be equal to the start date (1 day event) or chronologically subsequent. Both bounds are inclusive, and the format shown in the example above must be followed.

The markdown section of the meta file then contains the event's description. Descriptions are made available directly in the Discord guild as embeds sent by the Python bot. For formatting, use Discord's watered down Markdown ~ keep in mind that e.g. the `#` symbol does not create a heading.

A description is required to exist, and must be at most 2048 characters in length to fit into a Discord embed.

### `banners`

Directory with 1 or more assets to be used as the guild banner while the event is active.

If you're wondering about the desired dimensions, take a look at existing assets for reference.

### `server_icons`

Directory with 1 or more icon assets. The bot will automatically rotate icons from this directory at a configured frequency. Subdirectories in `server_icons` are simply ignored ~ only icons present directly in `server_icons` are considered.

If an event fails to satisfy these conditions, it will be ignored by Python.

## Reference event

Below is an example of a well configured event:

```
├── events/
│ ├── christmas/
│ │ ├── misc_assets/
│ │ │ ├── festive.svg
│ │ ├── server_icons/
│ │ │ ├── snowing.gif
│ │ │ ├── festive.png
│ │ ├── banners/
│ │ │ ├── green_and_red.png
│ │ │ ├── raindeer.png
│ │ ├── meta.md
│ │ ├── reindeer.mp4
```
```
---
start_date: December 1
end_date: December 25
---
**Christmas!**

I wonder what I'm getting this year!
```

In this case, on the 1st of December, the bot will:
* Apply `banner.png`
* Begin rotating `snowing.gif` and `festive.png`
* Send a `#changelog` notification with the event description

On the 26th, the transition into the next event takes place.

Files such as `festive.svg` and `reindeer.mp4` are simply ignored. The bot doesn't use them, but doesn't mind them being there.

## Automatic validation

Fortunately, it is not necessary to manually verify that all events are configured properly w.r.t. the requirements explained above. The `validation.py` script contains logic to ascertain correct setup, and will automatically run in CI on pull requests to prevent a broken configuration from reaching the production branch.

Validation happens in two stages. First, all events are checked individually, to ensure that they contain all necessary assets and have a correctly structured `meta.md` file. If all events pass, the second stage verifies that there is exactly 1 fallback event, and that no events collide. In the case of collision, the exact dates and culprit events are printed.

We depend on a minimal set of non-stdlib packages to parse meta files: [python-frontmatter](https://pypi.org/project/python-frontmatter/) wrapping around [pyyaml](https://pypi.org/project/PyYAML/). The exact version pins are provided in `requirements.txt` with the recommended Python version to use.

If you'd prefer to create a virtual environment with Pipenv, it is possible with the following command:

```
pipenv install -r events/requirements.txt
```

This will spawn a lockfile that you can sync from. Please make sure that you do not accidentally commit the Pipenv-generated files.
