import matplotlib.font_manager

fonts = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')

font_names = []
for f in fonts:
    try:
        font_names.append(matplotlib.font_manager.get_font(f).family_name)
    except RuntimeError:
        print(f"Warning: Could not process font: {f}")
        continue

# フォント名の一覧を表示
for name in sorted(set(font_names)):
    print(name)
