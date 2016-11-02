# flask
from flask import render_template
from flask import session

# local
from tinker import app
from tinker import sentry


def error_render_template(template_path, error, code=None):
    sentry.captureException()

    if code:  # Means that it's a handled error/exception
        if code == 500:  # No need to log 403s, 404s, or 503s
            app.logger.error("%s -- %s" % (session['username'], str(error)))

    else:  # Means it's an unhandled exception
        app.logger.error('Unhandled Exception: %s', str(error))
        code = 500  # To make sure that the return statement doesn't break

    return render_template(template_path,
                           sentry_event_id=sentry.last_event_id,
                           public_dsn=sentry.client.get_public_dsn('https')), code


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
