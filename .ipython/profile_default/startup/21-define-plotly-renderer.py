import plotly.io as pio

print("Setting plotly default renderer")
pio.renderers.default = "notebook+plotly_mimetype+pdf"
print(f"plotly default renderer set to '{pio.renderers.default}'")
