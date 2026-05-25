import reflex as rx

config = rx.Config(
    app_name="PostMeLater",
    frontend_packages=["es-toolkit@1.39.3"],
    plugins=[
        rx.plugins.TailwindV3Plugin(),
        rx.plugins.RadixThemesPlugin(theme=rx.theme(appearance="light")),
        rx.plugins.SitemapPlugin(),
    ],
)
