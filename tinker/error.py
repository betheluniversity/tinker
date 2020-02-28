# Packages
from flask import render_template, session

# Local
from tinker import app, sentry_sdk


def error_render_template(template_path, error, code=None):
    sentry_sdk.capture_exception()

    if code:  # Means that it's a handled error/exception
        if code in [500, 503]:  # No need to log 403s, 404s, or 503s
            if not app.config['UNIT_TESTING']:
                app.logger.error("%s -- %s" % (session['username'], str(error)))

    else:  # Means it's an unhandled exception
        app.logger.error('Unhandled Exception: %s', str(error))
        code = 500  # To make sure that the return statement doesn't break

    return render_template(template_path,
                           sentry_event_id=sentry_sdk.last_event_id(),
                           public_dsn=app.config['SENTRY_URL']), code


@app.errorhandler(403)
def permission_denied(e):
    return error_render_template('error/403.html', e, 403)


@app.errorhandler(404)
def page_not_found(e):
    return error_render_template('error/404.html', e, 404)


@app.errorhandler(500)
def server_error(e):
    return error_render_template('error/500.html', e, 500)


@app.errorhandler(503)
def transport_error(e):
    return error_render_template('error/503.html', e, 503)


@app.errorhandler(Exception)
def unhandled_exception(e):
    return error_render_template('error/500.html', e)
