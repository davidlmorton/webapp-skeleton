from webapp.logging_configuration import configure_web_logging
from webapp.api import application
from webapp import settings

app = application.create_app()
configure_web_logging()


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGINT))

    app.run(host=settings.host,
            port=settings.port,
            debug=False, use_reloader=False)
