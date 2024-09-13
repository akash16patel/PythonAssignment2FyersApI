from fyers_apiv3 import fyersModel as FM
if __name__=="__main__":

    client_id='FK9E8YPI2C-100'
    secret_key='4Z24S0WRKI'
    redirect_uri='https://www.google.com/'
    user_name="YA31758"
    pin=1998
    mobile=7004532485
    response_type="code"
    grant_type="authorization_code"

    session=FM.SessionModel(client_id=client_id, secret_key=secret_key, redirect_uri=redirect_uri, response_type=response_type, grant_type=grant_type)
    # response=session.generate_authcode()
    #
    # print(response)
    link="https://www.google.com/?s=ok&code=200&auth_code=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkubG9naW4uZnllcnMuaW4iLCJpYXQiOjE3MjYyNTI1NDAsImV4cCI6MTcyNjI4MjU0MCwibmJmIjoxNzI2MjUxOTQwLCJhdWQiOiJbXCJ4OjBcIiwgXCJ4OjFcIiwgXCJ4OjJcIiwgXCJkOjFcIiwgXCJkOjJcIiwgXCJ4OjFcIiwgXCJ4OjBcIl0iLCJzdWIiOiJhdXRoX2NvZGUiLCJkaXNwbGF5X25hbWUiOiJZQTMxNzU4Iiwib21zIjoiSzEiLCJoc21fa2V5IjoiNGJjY2YwYzBiOGYwYTAzMDVlZWVlMzgxNTdjOGYxMjVkZjg2YjI2OGRlMjE3NmEyOGRkZDBhYzgiLCJub25jZSI6IiIsImFwcF9pZCI6IkZLOUU4WVBJMkMiLCJ1dWlkIjoiYTI2MmVmNzI1NTAzNGIyZGJhMTA1NDBjYmQ2MTg2NTQiLCJpcEFkZHIiOiIwLjAuMC4wIiwic2NvcGUiOiIifQ.0ZtA39Ti3CnbkZxPWFF81i8rIpbsvGC6NTzzZxOvTxY&state=None"

    s1=link.split('auth_code=')
    auth_code=s1[1].split('&state')[0]
    session.set_token(auth_code)
    response=session.generate_token()
    print(response)
    access_token=response['access_token']
    with open('access.txt','w') as w:
        w.write(access_token)
    refresh_token=response['refresh_token']
    with open('refresh_token.txt','w') as w:
        w.write(refresh_token)
