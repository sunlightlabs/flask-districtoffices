from saucebrush import run_recipe
from saucebrush.emitters import DebugEmitter, CSVEmitter
from saucebrush.filters import FieldModifier, FieldRemover, FieldRenamer, Filter
from saucebrush.sources import CSVSource
import json
import os
import re
import requests

PWD = os.path.abspath(os.path.dirname(__file__))

WHITESPACE_RE = re.compile(r"\s+")

class GeocoderFilter(Filter):

    ENDPOINT = "http://where.yahooapis.com/geocode"

    def __init__(self, appid, field):
        super(GeocoderFilter, self).__init__()
        self.appid = appid
        self.field = field

    def geocode(self, address):

        params = {
            'q': address,
            'appid': self.appid,
            'flags': 'CJ',
        }

        resp = requests.get(self.ENDPOINT, params=params)
        data = json.loads(resp.content)

        try:

            result = data['ResultSet']['Results'][0]
            return (result['latitude'], result['longitude'])

        except KeyError:
            pass
        except IndexError:
            pass

        return (None, None)

    def process_record(self, record):

        ll = self.geocode(record['address'])

        record['latitude'] = ll[0]
        record['longitude'] = ll[1]

        return record

inpath = os.path.join(PWD, 'data', 'directory-original.csv')
outpath = os.path.join(PWD, 'data', 'directory-clean.csv')

run_recipe(
    CSVSource(open(inpath, 'r')),
    FieldRemover(('First','Middle','Last','District: Fax','Initial ')),
    FieldRenamer({
        'bioguide_id': 'Bio ID',
        'address': 'District: Address',
        'phone': 'District: Phone',
    }),
    FieldModifier(('bioguide_id','address','phone'), lambda s: s.strip()),
    FieldModifier('address', lambda s: WHITESPACE_RE.sub(' ', s)),
    GeocoderFilter('Kv3.btLV34EuebZGMzi1KaqI_BOPhPjx7FtbvED.umr8DGUq0NysoGN0XIIIDRU-', 'address'),
    DebugEmitter(),
    CSVEmitter(open(outpath, 'w'), ('bioguide_id','address','latitude','longitude','phone')),
)