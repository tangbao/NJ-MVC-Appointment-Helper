from utils.secret import *

# token of the bot
TOKEN = load_secret('token')

AUTHORIZED_USERS = load_secrets('authorized_users')

MVC_URL = 'https://telegov.njportal.com/njmvc/AppointmentWizard/'
PRJ_URL = 'https://github.com/tangbao/NJ-MVC-Appointment-Helper/'
LOCATION_ID_URL = 'https://github.com/tangbao/NJ-MVC-Appointment-Helper/blob/master/location_list.md'

SERVICE_ID = {
    'INITIAL PERMIT (NOT FOR KNOWLEDGE TEST)': '15',
    'CDL PERMIT OR ENDORSEMENT - (NOT FOR KNOWLEDGE TEST)': '14',
    'REAL ID': '12',
    'NON-DRIVER ID': '16',
    'KNOWLEDGE TESTING': '17',
    'RENEWAL: LICENSE OR NON-DRIVER ID': '11',
    'RENEWAL: CDL': '6',
    'TRANSFER FROM OUT OF STATE': '7',
    'NEW TITLE OR REGISTRATION': '8',
    'SENIOR NEW TITLE OR REGISTRATION (65+)': '9',
    'REGISTRATION RENEWAL': '10',
    'TITLE DUPLICATE/REPLACEMENT': '13'
}

SERVICE_KEYBOARD = [['INITIAL PERMIT (NOT FOR KNOWLEDGE TEST)', 'KNOWLEDGE TESTING', 'REAL ID'],
                    ['CDL PERMIT OR ENDORSEMENT - (NOT FOR KNOWLEDGE TEST)', 'NON-DRIVER ID'],
                    ['RENEWAL: LICENSE OR NON-DRIVER ID', 'RENEWAL: CDL', 'TRANSFER FROM OUT OF STATE'],
                    ['NEW TITLE OR REGISTRATION', 'SENIOR NEW TITLE OR REGISTRATION (65+)'],
                    ['REGISTRATION RENEWAL', 'TITLE DUPLICATE/REPLACEMENT']]

LOCATION_ID = {'186': 'Bakers Basin', '187': 'Bayonne', '189': 'Camden', '208': 'Cardiff', '191': 'Delanco',
               '192': 'Eatontown', '194': 'Edison', '195': 'Flemington', '197': 'Freehold', '198': 'Lodi',
               '200': 'Newark', '201': 'North Bergen', '203': 'Oakland', '204': 'Paterson', '206': 'Rahway',
               '207': 'Randolph', '188': 'Rio Grande', '190': 'Salem', '193': 'South Plainfield', '196': 'Toms River',
               '199': 'Vineland', '202': 'Wayne', '205': 'West Deptford', '163': 'Bakers Basin', '164': 'Bayonne',
               '166': 'Camden', '185': 'Cardiff', '168': 'Delanco', '169': 'Eatontown', '171': 'Edison',
               '172': 'Flemington', '174': 'Freehold', '175': 'Lodi', '177': 'Newark', '178': 'North Bergen',
               '180': 'Oakland', '181': 'Paterson', '183': 'Rahway', '184': 'Randolph', '165': 'Rio Grande',
               '167': 'Salem', '170': 'South Plainfield', '173': 'Toms River', '176': 'Vineland', '179': 'Wayne',
               '182': 'West Deptford', '124': 'Bakers Basin', '125': 'Bayonne', '127': 'Camden', '146': 'Cardiff ',
               '129': 'Delanco', '130': 'Eatontown', '132': 'Edison', '133': 'Flemington', '135': 'Freehold',
               '136': 'Lodi', '138': 'Newark', '139': 'North Bergen', '141': 'Oakland', '142': 'Paterson',
               '144': 'Rahway', '145': 'Randolph', '126': 'Rio Grande', '128': 'Salem', '131': 'South Plainfield',
               '134': 'Toms River', '137': 'Vineland', '140': 'Wayne', '143': 'West Deptford', '209': 'Bakers Basin',
               '210': 'Bayonne', '212': 'Camden', '231': 'Cardiff', '214': 'Delanco', '215': 'Eatontown',
               '217': 'Edison', '218': 'Flemington', '220': 'Freehold', '221': 'Lodi', '223': 'Newark',
               '224': 'North Bergen', '226': 'Oakland', '227': 'Paterson', '229': 'Rahway', '230': 'Randolph',
               '211': 'Rio Grande', '213': 'Salem', '216': 'South Plainfield', '219': 'Toms River', '222': 'Vineland',
               '225': 'Wayne', '228': 'West Deptford', '232': 'Bakers Basin', '233': 'Bayonne', '235': 'Camden',
               '254': 'Cardiff', '237': 'Delanco', '238': 'Eatontown', '240': 'Edison', '241': 'Flemington',
               '243': 'Freehold', '244': 'Lodi', '246': 'Newark', '247': 'North Bergen', '249': 'Oakland',
               '250': 'Paterson', '252': 'Rahway', '253': 'Randolph', '234': 'Rio Grande', '236': 'Salem',
               '239': 'South Plainfield', '242': 'Toms River', '245': 'Vineland', '248': 'Wayne',
               '251': 'West Deptford', '101': 'Bakers Basin', '102': 'Bayonne', '104': 'Camden', '105': 'Cardiff ',
               '107': 'Delanco', '108': 'Eatontown', '110': 'Edison', '111': 'Flemington', '113': 'Freehold',
               '114': 'Lodi', '116': 'Newark', '117': 'North Bergen', '119': 'Oakland', '120': 'Paterson',
               '122': 'Rahway', '123': 'Randolph', '103': 'Rio Grande', '106': 'Salem', '109': 'South Plainfield',
               '112': 'Toms River', '115': 'Vineland', '118': 'Wayne', '121': 'West Deptford', '7': 'Bakers Basin',
               '8': 'Bayonne', '10': 'Camden', '11': 'Cardiff', '13': 'Delanco', '14': 'Eatontown', '16': 'Edison',
               '17': 'Flemington', '19': 'Freehold', '20': 'Lodi', '22': 'Newark', '23': 'North Bergen',
               '25': 'Oakland', '26': 'Paterson', '28': 'Rahway', '29': 'Randolph', '9': 'Rio Grande', '12': 'Salem',
               '15': 'South Plainfield', '18': 'Toms River', '21': 'Vineland', '24': 'Wayne', '27': 'West Deptford',
               '46': 'Bakers Basin', '47': 'Bayonne', '49': 'Camden', '48': 'Cardiff', '50': 'Delanco',
               '51': 'Eatontown', '52': 'Edison', '53': 'Flemington', '54': 'Freehold', '55': 'Lodi', '56': 'Newark',
               '57': 'North Bergen', '58': 'Oakland', '59': 'Paterson', '60': 'Rahway', '61': 'Randolph',
               '62': 'Rio Grande', '64': 'Salem', '63': 'South Plainfield', '65': 'Toms River', '66': 'Vineland',
               '67': 'Wayne', '68': 'West Deptford', '30': 'Cherry Hill', '31': 'East Orange', '32': 'Hazlet',
               '33': 'Jersey City', '34': 'Lakewood', '35': 'Manahawkin', '36': 'Medford', '37': 'Newton',
               '256': 'Rio Grande', '38': 'Runnemede', '39': 'Somerville', '40': 'South Brunswick', '41': 'Springfield',
               '42': 'Trenton Regional', '43': 'Turnersville', '44': 'Wallington', '45': 'Washington',
               '79': 'Manahawkin', '71': 'Somerville', '85': 'Cherry Hill', '86': 'East Orange', '87': 'Hazlet',
               '88': 'Jersey City', '89': 'Lakewood', '90': 'Manahawkin', '91': 'Medford', '92': 'Newton',
               '257': 'Rio Grande', '93': 'Runnemede', '94': 'Somerville', '95': 'South Brunswick', '96': 'Springfield',
               '97': 'Trenton Regional', '98': 'Turnersville', '99': 'Wallington', '100': 'Washington',
               '147': 'Cherry Hill', '148': 'East Orange', '149': 'Hazlet', '150': 'Jersey City', '151': 'Lakewood',
               '152': 'Manahawkin', '153': 'Medford', '154': 'Newton', '255': 'Rio Grande', '155': 'Runnemede',
               '156': 'Somerville', '157': 'South Brunswick', '158': 'Springfield', '159': 'Trenton Regional',
               '160': 'Turnersville', '161': 'Wallington', '162': 'Washington', '0': 'All'}
