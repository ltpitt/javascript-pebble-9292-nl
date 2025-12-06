from waflib.Configure import conf


@conf
def appinfo_bitmap_to_png(ctx, appinfo_json):
    # New Rebble SDK supports bitmap resources natively
    # This conversion is no longer needed
    pass
