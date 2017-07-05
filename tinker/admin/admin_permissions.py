from flask import session, abort, request


def admin_permissions(self, route_base, *args):
    if route_base != '/admin/redirect' or route_base != '/admin/program-search':
        if 'Administrators' not in session['groups']:
            abort(403)

    if route_base == '/admin/program-search':
        # give access to admins and lauren
        if 'Administrators' not in session['groups'] and 'parlau' not in session['groups'] and session['username'] != 'kaj66635':
            abort(403)

    if route_base == '/admin/redirect':
        if '/public/' in request.path:
            return

        # Checks to see what group the user is in
        if 'Tinker Redirects' not in session['groups'] and 'Administrators' not in session['groups']:
            abort(403)
