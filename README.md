# File Upload App using Flask

> This is a work-in-progress demo. If it works out, a LICENSE will be added when it is done. Otherwise this repository will probably go away.

<sub>2022-10-18</sub>

## Notes

Using **Visual Studio Code** with the [cornflakes-linter](https://marketplace.visualstudio.com/items?itemName=kevinglasson.cornflakes-linter) and [Better Jinja](https://marketplace.visualstudio.com/items?itemName=samuelcolvin.jinjahtml) extensions.

Added settings to the `.vscode/settings.json` file for the project (not in repo).

The `python.formatting.blackArgs` setting in this fragment overrides some of the **black** formatter's defaults:

```json
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": [
        "--skip-string-normalization",
        "--line-length",
        "79"
    ],
```

This fragment tells **Better Jinja** to treat HTML files as Jinja2 templates:

```json
    "files.associations": {
        "*.html": "jinja-html"
      }
```
