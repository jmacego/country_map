from flask import Flask, jsonify, render_template, request, Blueprint, redirect, url_for, session, make_response, session, current_app
from requests_oauthlib import OAuth2Session
import json
import uuid
import os
import secrets
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode
from ..models.auth import require_email_authorization

# Load environment variables
load_dotenv()
from app.auth import bp

@bp.route('/authorize/<provider>')
def oauth2_authorize(provider):
    """
    Initiate OAuth2 authorization for a specified provider.

    This endpoint initiates the OAuth2 authorization process for a given provider. It generates a state token for security, constructs a query string with OAuth2 parameters, and redirects the user to the provider's authorization URL.

    Args:
        provider (str): The name of the OAuth2 provider to authorize.

    Returns:
        werkzeug.wrappers.Response: A redirect response to the OAuth2 provider's authorization URL with the necessary query parameters.

    Raises:
        HTTPException: An HTTP 404 error if the provider is not configured.
    """
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # generate a random string for the state parameter
    session['oauth2_state'] = secrets.token_urlsafe(16)

    # create a query string with all the OAuth2 parameters
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('auth.oauth2_callback', provider=provider,
                                _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    # redirect the user to the OAuth2 provider authorization URL
    return redirect(provider_data['authorize_url'] + '?' + qs)

@bp.route('/callback/<provider>')
def oauth2_callback(provider):
    """
    Handle the OAuth2 callback from the provider.

    This endpoint processes the callback after a user has authenticated with an OAuth2 provider. It validates the state parameter, exchanges the authorization code for an access token, and retrieves the user's email address using the access token. If any step fails, it aborts the process with the appropriate error code.

    Args:
        provider (str): The name of the OAuth2 provider.

    Returns:
        werkzeug.wrappers.Response: A redirect response to the 'world_map' view if successful, or an error response if any step of the authentication process fails.

    Raises:
        HTTPException: An HTTP 404 error if the provider is not configured, a 401 error if there is an authentication error, or if the state parameter or authorization code is invalid.
    """
    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # if there was an authentication error, flash the error messages and exit
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('travel.world_map'))

    # make sure that the state parameter matches the one we created in the
    # authorization request
    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    # make sure that the authorization code is present
    if 'code' not in request.args:
        abort(401)

    # exchange the authorization code for an access token
    response = requests.post(provider_data['token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('auth.oauth2_callback', provider=provider,
                                _external=True),
    }, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)

    # use the access token to get the user's email address
    response = requests.get(provider_data['userinfo']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })
    if response.status_code != 200:
        abort(401)
    email = provider_data['userinfo']['email'](response.json())

    session['email'] = email
    return redirect(url_for('travel.world_map'))

@bp.route('/email')
def email():
    """Test route. Display e-mail user is logged in as"""
    if session.get('email'):
        return(session.get('email'))
    return("Unauthenticated")