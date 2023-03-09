import requests
import json


class RestApiClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def _get_request(self, url, params=None):
        try:
            headers = {'accept': 'application/json'}
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return json.loads(response.text)
        except requests.exceptions.RequestException as e:
            error = {'success': False,
                     'message': str(e)}
            return error
        except Exception as e:
            error = {'success': False,
                     'message': str(e)}
            return error

    def _post_request(self, url, data=None):
        try:
            headers = {'accept': 'application/json'}
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return json.loads(response.text)
        except requests.exceptions.RequestException as e:
            error = {'success': False,
                     'message': str(e)}
            return error
        except Exception as e:
            error = {'success': False,
                     'message': str(e)}
            return error

    def _delete_request(self, url, params=None):
        try:
            headers = {'accept': 'application/json'}
            response = requests.delete(url, params=params, headers=headers)
            response.raise_for_status()
            return json.loads(response.text)
        except requests.exceptions.RequestException as e:
            error = {'success': False,
                     'message': str(e)}
            return error
        except Exception as e:
            error = {'success': False,
                     'message': str(e)}
            return error

    def get(self, endpoint, params=None):
        url = self.base_url + endpoint
        return self._get_request(url, params)

    def post(self, endpoint, data=None):
        url = self.base_url + endpoint
        return self._post_request(url, data)

    def delete(self, endpoint, params=None):
        url = self.base_url + endpoint
        return self._delete_request(url, params)