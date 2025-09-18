import argparse
from astropy.io import ascii
from astropy.table import Table
import datetime
import json
import matplotlib.pyplot as plt 

# =============================================================================
# USER VARIABLES
# =============================================================================

parser = argparse.ArgumentParser(description='Parse user inputs, sometimes overwriting defaults')

# Schedule File, Colours, and size parameters

parser.add_argument('--year', type=str, help='', required=True)
parser.add_argument('--team', type=str, help='', required=True)

parser.add_argument('--fn', type=str, help='Schedule file. Currently must be a .csv with the MLB formatting', required=False)
parser.add_argument('--config_file', type=str, help='JSON file with variables')

parser.add_argument('--start', type=int, help='Line of the schedule to start the regular season. Default is 33, from the current MLB test schedules.') # default=33)

parser.add_argument('--hfc', type=str, help='Home Fill Colour') # 
parser.add_argument('--htc', type=str, help='Home Text Colour') # 

parser.add_argument('--afc', type=str, help='Away Fill Colour') # 
parser.add_argument('--atc', type=str, help='Away Text Colour') # 

parser.add_argument('--ofc', type=str, help='Off Day Fill Colour') # 
parser.add_argument('--otc', type=str, help='Off Day Text Colour')

parser.add_argument('--head_colour', type=str, help='Header Text Colour')

parser.add_argument('--asg', type=str, help='All-Star Game date in mm/dd/yyyy format')
parser.add_argument('--asg_fill', type=str, help='ASG font colour') # 
parser.add_argument('--asg_font', type=str, help='ASG fill colour') # 
parser.add_argument('--asg_location', type=str, help='')

parser.add_argument('--tbc', type=str, help='Ticket Box Colour') # 
parser.add_argument('--highlight_file', type=str, help='')

parser.add_argument('--weekstart', type=int, help='Week starts on Sunday = 6, Monday = 0') # 

parser.add_argument('--legend_month', type=int, help='IE, the legend goes under this month') # 
parser.add_argument('--legend_scale', type=float, help='Scale of the legend relative to calendar cells') # 

parser.add_argument('--hour_format', type=str, help='Hour format for the start times. String inputs of "12" or "I" will set 12-hour time format, anything else will be 24-hour') # 
parser.add_argument('--ampm', type=bool, help='Include AM/PM in the game start times. Default is False.')

parser.add_argument('--rows', type=int, help='')
parser.add_argument('--columns', type=int, help='')

parser.add_argument('--fh', type=float, help='Ideal figure height (any unit, see \'unit_scale\')') # 
parser.add_argument('--fw', type=float, help='Ideal figure width (any unit, see \'unit_scale\')') # 
parser.add_argument('--unit_scale', type=float, help='Scale the figure size to be a given unit, 1.25 for inches or 0.49 for cm. (Python takes inches, but empirically not true inches!)')

parser.add_argument('--v_margin', type=float, help='Vertical margin')
parser.add_argument('--h_margin', type=float, help='Horizontal margin')

parser.add_argument('--cell_width', type=float, help='The width of the date cells. The default behaviour is to set it by the desired schedule width and number of month columns, for two columns & 8.5 inches, it works out to ~0.572')
parser.add_argument('--cell_height', type=float, help='The height of the date cells. The default behaviour is to use a 4/5 ratio with the cell width. It works out to ~0.458 in the default settings')

parser.add_argument('--gfs', type=float, help='Game font size')
parser.add_argument('--dfs', type=float, help='Date font size')
parser.add_argument('--mfs', type=float, help='Month font size')

parser.add_argument('--hfs', type=float, help='Header font size')

parser.add_argument('--header_add', type=float, help='Added space above the calendar section for the cells')

parser.add_argument('--month_add', type=float, help='Added space between the month rows')

parser.add_argument('--m4x', type=float, help='Move March/April left or right, in units of cell width. The default of zero corresponds to the location set by the above parameters.')
parser.add_argument('--m4y', type=float, help='Move March/April up or down, in units of cell height. The default of zero corresponds to the location set by the above parameters.')

parser.add_argument('--m5x', type=float, help='Move May left or right, in units of cell width. The default of zero corresponds to the location set by the above parameters.')
parser.add_argument('--m5y', type=float, help='Move May up or down, in units of cell height. The default of zero corresponds to the location set by the above parameters.')

parser.add_argument('--m6x', type=float, help='Move June left or right, in units of cell width. The default of zero corresponds to the location set by the above parameters.')
parser.add_argument('--m6y', type=float, help='Move June up or down, in units of cell height. The default of zero corresponds to the location set by the above parameters.')

parser.add_argument('--m7x', type=float, help='Move July left or right, in units of cell width. The default of zero corresponds to the location set by the above parameters.')
parser.add_argument('--m7y', type=float, help='Move July up or down, in units of cell height. The default of zero corresponds to the location set by the above parameters.')

parser.add_argument('--m8x', type=float, help='Move August left or right, in units of cell width. The default of zero corresponds to the location set by the above parameters.')
parser.add_argument('--m8y', type=float, help='Move August up or down, in units of cell height. The default of zero corresponds to the location set by the above parameters.')

parser.add_argument('--m9x', type=float, help='Move September left or right, in units of cell width. The default of zero corresponds to the location set by the above parameters.')
parser.add_argument('--m9y', type=float, help='Move September up or down, in units of cell height. The default of zero corresponds to the location set by the above parameters.')

parser.add_argument('--legend_add', type=float, help='Added space for the legend')
parser.add_argument('--legend_x_shift', type=float, help='Move legend left or right, in units of cell width. The default of zero corresponds to the location set by the above parameters.')

parser.add_argument('--frame_on', type=float, help='Show the frame of the desired figure size, with units. This is helpful for fine-tuning sizes.')
parser.add_argument('--abbvs', type=str, help='JSON file with the three letter abbreviations for the nicknames in the MLB schedule.')

# Parse arguments
args = parser.parse_args()

config = {}
if args.config_file:
    try:
        with open(args.config_file, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")

# Resolve command line versus JSON
year = args.year # if args.year is not None else config.get('year', '') # Making these required
team = args.team # if args.team is not None else config.get('team', '')

fn = args.fn if args.fn is not None else config.get('fn', f'{year}{team}Schedule.csv')
start = args.start if args.start is not None else config.get('start', 0)

asg = args.asg if args.asg is not None else config.get('asg', '01/01/2001')
asg_fill = args.asg_fill if args.asg_fill is not None else config.get('asg_fill', '') # ASG font colour
asg_font = args.asg_font if args.asg_font is not None else config.get('asg_font', '') # ASG fill colour
asg_location = args.asg_location if args.asg_location is not None else config.get('asg_location', '')

hfc = args.hfc if args.hfc is not None else config.get('hfc', 'xkcd:royal blue') # Home Fill Colour
htc = args.htc if args.htc is not None else config.get('htc', 'xkcd:white') # Home Text Colour

afc = args.afc if args.afc is not None else config.get('afc', 'xkcd:sky blue') # Away Fill Colour
atc = args.atc if args.atc is not None else config.get('atc', 'xkcd:white') # Away Text Colour

ofc = args.ofc if args.ofc is not None else config.get('ofc', 'xkcd:light grey') # Off Day Fill Colour
otc = args.otc if args.otc is not None else config.get('otc', 'xkcd:navy blue') # Off Day Text Colour

head_colour = args.head_colour if args.head_colour is not None else config.get('head_colour', 'xkcd:navy blue') # Off Day Text Colour

tbc = args.tbc if args.tbc is not None else config.get('tbc', 'xkcd:goldenrod') # Ticket Box Colour
highlight_file = args.highlight_file if args.highlight_file is not None else config.get('highlight_file')#, '2025_tickets.txt')

abbvs = args.abbvs if args.abbvs is not None else config.get('abbvs', 'nickname_to_abbreviation_traditional.json')

weekstart = args.weekstart if args.weekstart is not None else config.get('weekstart', 0) # Week starts on Sunday = 6, Monday = 0

legend_month = args.legend_month if args.legend_month is not None else config.get('legend_month', 7) # IE, the legend goes under this month
legend_scale = args.legend_scale if args.legend_scale is not None else config.get('legend_scale', 0.75) # Scale of the legend relative to calendar cells

hour_format = args.hour_format if args.hour_format is not None else config.get('hour_format', '24') # '12' or '24' Defaults to '24' if neither of these.
ampm = args.ampm if args.ampm is not None else config.get('ampm', False)

fh = args.fh if args.fh is not None else config.get('fh', 11.0) # Ideal figure height
fw = args.fw if args.fw is not None else config.get('fw', 8.5) # Ideal figure width
rows = args.rows if args.rows is not None else config.get('rows', 3)
columns = args.columns if args.columns is not None else config.get('columns', 2)

unit_scale = args.unit_scale if args.unit_scale is not None else config.get('unit_scale', 1.25)

v_margin = args.v_margin if args.v_margin is not None else config.get('v_margin', 0.1)
h_margin = args.h_margin if args.h_margin is not None else config.get('h_margin', 0.1)

# Fine-tuning parameters to make it actually look good

cell_width = args.cell_width if args.cell_width is not None else config.get('cell_width', (fw - 2*h_margin) / (7*columns + 0.5*(columns-1))) # Each month is seven days wide, plus half a day's width between the months
cell_height = args.cell_height if args.cell_height is not None else config.get('cell_height', (cell_width * 2) / 2.5)

gfs = args.gfs if args.gfs is not None else config.get('gfs', cell_height*25) # Game font size
dfs = args.dfs if args.dfs is not None else config.get('dfs', 0.5*gfs) # Date font size
mfs = args.mfs if args.mfs is not None else config.get('mfs', 2*gfs) # Month font size

hfs = args.hfs if args.hfs is not None else config.get('hfs', min([fw*3, fh*4])) # Header font size

header_add = args.header_add if args.header_add is not None else config.get('header_add', v_margin + hfs/72)

spare_height = fh - v_margin*2 - hfs/72 - (cell_height * (rows*6)) # Six weeks to a month, plus 1.5 between each row. It simplifies to r*7 - 1 = 6r + 1.5*(r-1)

month_add = args.month_add if args.month_add is not None else config.get('month_add', spare_height*0.4)

frame_on = args.frame_on if args.frame_on is not None else config.get('frame_on', False)

m4x = args.m4x if args.m4x is not None else config.get('m4x', 0)
m4y = args.m4y if args.m4y is not None else config.get('m4y', 0)

m5x = args.m5x if args.m5x is not None else config.get('m5x', 0)
m5y = args.m5y if args.m5y is not None else config.get('m5y', 0)

m6x = args.m6x if args.m6x is not None else config.get('m6x', 0)
m6y = args.m6y if args.m6y is not None else config.get('m6y', 0)

m7x = args.m7x if args.m7x is not None else config.get('m7x', 0)
m7y = args.m7y if args.m7y is not None else config.get('m7y', 0)

m8x = args.m8x if args.m8x is not None else config.get('m8x', 0)
m8y = args.m8y if args.m8y is not None else config.get('m8y', 0)

m9x = args.m9x if args.m9x is not None else config.get('m9x', 0)
m9y = args.m9y if args.m9y is not None else config.get('m9y', 0)

legend_add = args.legend_add if args.legend_add is not None else config.get('legend_add', 0)
legend_x_shift = args.legend_x_shift if args.legend_x_shift is not None else config.get('legend_x_shift', 0)

# =============================================================================
# Read in and format text file
# =============================================================================

if type(highlight_file) == str and highlight_file != '':
    try:
        highlights = open(highlight_file).readlines()
        for i in range(len(highlights)):
            highlights[i] = highlights[i][:-1]
    except OSError:
        highlights = None
        print('Highlight file not found, ignoring.')
else:
    highlights = None
    
def _reformatMLBSchedule(fn, team, asg, start, hour_format, ampm, highlights=None):
    if ampm == True:
        ampm_format = ' %p'
    else:
        ampm_format = ''
    
    textschedule = ascii.read(fn)
    schedule2025 = textschedule[start:]
    
    openingday = datetime.datetime.strptime(f'{schedule2025["START DATE"][0]}', '%m/%d/%y').toordinal()
    asg_ordinal = datetime.datetime.strptime(asg, '%d/%m/%Y').toordinal()
    closingday = datetime.datetime.strptime(f'{schedule2025["START DATE"][-1]}', '%m/%d/%y').toordinal()
    
    asciischedule = Table(names=['ordinal_date', 'string_date', 'opponent', 'location', 'start_time', 'highlight'], dtype=[int, 'S10', 'S15', 'S1', 'S5', bool])
    
    for i in range(openingday, closingday+1, 1):
        sched_date = schedule2025[schedule2025['START DATE'] == datetime.date.fromordinal(i).strftime('%m/%d/%y')]
        
        if len(sched_date) == 1:
            sched_date = sched_date[0]
            if sched_date['START TIME'].dtype != float:
                gamedatetime = datetime.datetime.strptime(sched_date['START DATE'] + ' ' + sched_date['START TIME'], '%m/%d/%y %I:%M %p')
            else:
                gamedatetime = datetime.datetime.strptime(sched_date['START DATE'], '%m/%d/%y')
            
            matchup = sched_date['SUBJECT'].split(' - ')[0]
            awayteam, hometeam = matchup.split(' at ')
            
            if hometeam == team:
                loc = 'H'
                opp = awayteam
            else:
                loc = 'A'
                opp = hometeam
        elif i == asg_ordinal:
            loc = ''
            opp = 'ALL-STAR GAME'
            
        else:
            gamedatetime = datetime.datetime.fromordinal(i)
            loc = ''
            opp = 'OFF DAY'
        
        if type(highlights) in [list, tuple] and gamedatetime.strftime('%d/%m/%Y') in highlights:
            highlight = True
        else:
            highlight = False
        
        if str(hour_format) not in ['12', 'I', '%I']:
            timestring = gamedatetime.strftime('%H:%M')
        else:
            if gamedatetime.strftime('%I:%M %p')[0] == '0':
                timestring = gamedatetime.strftime('%I:%M'+ampm_format)[1:]
            else:
                timestring = gamedatetime.strftime('%I:%M'+ampm_format)
        
        asciischedule.add_row([i, gamedatetime.strftime('%d/%m/%Y'), opp, loc, timestring, highlight])
    
    return asciischedule

# =============================================================================
# SET IMPORTANT DATES AND LOAD ABBREVIATIONS
# =============================================================================

ascii_sched = _reformatMLBSchedule(fn, team, asg, start, hour_format, ampm, highlights=highlights)

nickname_to_abbreviation_dict = json.load(open(abbvs))

# =============================================================================
# Make Calendar Schedule
# =============================================================================
months = {3:'March/April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September'}
weekdays = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}


fig = plt.figure()
fig.set_size_inches(h=fh*unit_scale, w=fw*unit_scale)
ax = fig.add_subplot(111)
ax.set_xlim(0, fw)
ax.set_ylim(-fh, 0)
ax.set_aspect('equal')
if not frame_on:
    ax.set_axis_off()

#cell_height = 2
#cell_width = 3
# Set the cell height and width based off the figure size

# Header
ax.text(fw*0.5, -v_margin, f'{year} {team} Schedule'.upper(), fontsize=hfs, color=head_colour, horizontalalignment='center', verticalalignment='top', fontweight='bold')

column = 0
row = cell_height

# Define the anchor points for each month
month_anchors = {3: [h_margin + m4x*cell_width, v_margin - header_add - month_add + m4y*cell_height], 4: [h_margin+m4x*cell_width, v_margin - header_add - month_add - 1*cell_height + m4y*cell_height]} # This will always be true
month_shifts_x = {5: m5x*cell_width, 6: m6x*cell_width, 7: m7x*cell_width, 8: m8x*cell_width, 9: m9x*cell_width}
month_shifts_y = {5: m5y*cell_height, 6: m6y*cell_height, 7: m7y*cell_height, 8: m8y*cell_height, 9: m9y*cell_height}
for month_number in range(5, 10):
    monthcol = (month_number - 4)//rows
    monthrow = (month_number - 4)%rows
    # Note that the number of columns is actually not used here.
    # This allows an arbitrary number of months, though it's unlikely to ever not be six.
    # It will run down a column until it hits the maximum number of rows, or runs out of months
    month_anchors[month_number] = [h_margin + (7.5*cell_width)*monthcol + month_shifts_x[month_number], v_margin - header_add - month_add*(1 + monthrow) - (6*cell_height)*monthrow + month_shifts_y[month_number]]

current_month = 3
# Month and week headers
for month_ordinal in months.keys():
    ax.text(month_anchors[month_ordinal][0]+cell_width*3.5, month_anchors[month_ordinal][1]+1*cell_height, months[month_ordinal].upper(), fontsize=mfs, color=head_colour, horizontalalignment='center', verticalalignment='center', fontweight='bold')
    for day in weekdays.keys():
        ax.text(month_anchors[month_ordinal][0] + (day - weekstart)%7*cell_width + 0.5*cell_width, month_anchors[month_ordinal][1]+0.25*cell_height, weekdays[day].upper(), color=otc, fontsize=dfs, horizontalalignment='center', verticalalignment='center')

ascii_sched.sort('ordinal_date') # It should already be, but just in case

for entry in ascii_sched.iterrows():
    date = datetime.date.fromordinal(entry[0])
    week_ordinal = (date.weekday() - weekstart)%7
    
    if entry[3] == 'H':
        fillcolour = hfc
        textcolour = htc
        opp = nickname_to_abbreviation_dict[entry[2]]
        if entry[4] != '00:00':
            starttime = entry[4]
        else:
            starttime = ''
        
    elif entry[3] == 'A':
        fillcolour = afc
        textcolour = atc
        opp = nickname_to_abbreviation_dict[entry[2]]
        if entry[4] != '00:00':
            starttime = entry[4]
        else:
            starttime = ''
            
    elif entry[2] == 'ALL-STAR GAME':
        fillcolour = asg_fill
        textcolour = asg_font
        starttime = asg_location.upper()
        #opp = 'ALL-STAR BREAK'
        opp = 'ASG'
        
    else:
        fillcolour = ofc
        textcolour = otc
        starttime = ''
        opp = ''
    
    if entry[5] == True:
        ec = tbc
        zo = 10
    else:
        ec = 'w'
        zo = 2
    
    if date.month != current_month:
        row = cell_height
        current_month = date.month
    
    elif week_ordinal == 0: # The elif is to stop it catching when the month starts on the first day of the week
        row += cell_height
    
    # Define the cell centre based on the day of the month
    # The month anchor is always the top left corner of the first IDEAL cell
    #     That is, the first cell that COULD BE present in the month, not necessarily the actual first
    x_centre = month_anchors[date.month][0] + week_ordinal * cell_width + 0.5*cell_width
    y_centre = month_anchors[date.month][1] - row + 0.5*cell_height
    
    # Plot the cell normal cell border
    ax.plot([x_centre-cell_width/2.0, x_centre-cell_width/2.0], [y_centre-cell_height/2.0, y_centre+cell_height/2.0], c=ec, lw=gfs/6, zorder=zo)
    ax.plot([x_centre+cell_width/2.0, x_centre+cell_width/2.0], [y_centre-cell_height/2.0, y_centre+cell_height/2.0], c=ec, lw=gfs/6, zorder=zo)
    ax.plot([x_centre-cell_width/2.0, x_centre+cell_width/2.0], [y_centre-cell_height/2.0, y_centre-cell_height/2.0], c=ec, lw=gfs/6, zorder=zo)
    ax.plot([x_centre-cell_width/2.0, x_centre+cell_width/2.0], [y_centre+cell_height/2.0, y_centre+cell_height/2.0], c=ec, lw=gfs/6, zorder=zo)
    
    # Fill the cell with the appropriate colour
    ax.fill((x_centre-cell_width/2.0, x_centre-cell_width/2.0, x_centre+cell_width/2.0, x_centre+cell_width/2.0, x_centre-cell_width/2.0), (y_centre-cell_height/2.0, y_centre+cell_height/2.0, y_centre+cell_height/2.0, y_centre-cell_height/2.0, y_centre-cell_height/2.0), fillcolour)
    
    # Cell text
    # Date (upper left)
    ax.text(x_centre-cell_width/2.0+cell_width*0.06, y_centre+cell_height/2.0-cell_height*0.1, date.day, color=textcolour, fontsize=dfs, verticalalignment='top')
    # Opponent (centred, bold)
    ax.text(x_centre, y_centre, opp, fontsize=gfs, color=textcolour, fontweight='bold', horizontalalignment='center', verticalalignment='center')
    # Start time (lower centre) (lower is here set at 20% of the cell's height)
    ax.text(x_centre, y_centre-(cell_height*(0.5 - 0.2)), starttime, fontsize=dfs, color=textcolour, fontweight='bold', horizontalalignment='center', verticalalignment='center')

# Legend boxes
# home_legend_loc = [month_anchors[7][0]+2*cell_width, month_anchors[7][1]-7*cell_height]
# away_legend_loc = [month_anchors[7][0]+5*cell_width, month_anchors[7][1]-7*cell_height]

home_legend_loc = [fw/2.0-1.5*cell_width*legend_scale + legend_x_shift*cell_width, month_anchors[legend_month][1]-5.85*cell_height + legend_add*cell_height]
away_legend_loc = [fw/2.0+1.5*cell_width*legend_scale + legend_x_shift*cell_width, month_anchors[legend_month][1]-5.85*cell_height + legend_add*cell_height]

ax.fill((home_legend_loc[0]-cell_width*legend_scale/2.0, home_legend_loc[0]-cell_width*legend_scale/2.0, home_legend_loc[0]+cell_width*legend_scale/2.0, home_legend_loc[0]+cell_width*legend_scale/2.0, home_legend_loc[0]-cell_width*legend_scale/2.0), (home_legend_loc[1]-cell_height*legend_scale/2.0, home_legend_loc[1]+cell_height*legend_scale/2.0, home_legend_loc[1]+cell_height*legend_scale/2.0, home_legend_loc[1]-cell_height*legend_scale/2.0, home_legend_loc[1]-cell_height*legend_scale/2.0), hfc)
ax.text(home_legend_loc[0]+0.75*cell_width*legend_scale, home_legend_loc[1], 'HOME', color=otc, fontsize=gfs, fontweight='bold', verticalalignment='center')

ax.fill((away_legend_loc[0]-cell_width*legend_scale/2.0, away_legend_loc[0]-cell_width*legend_scale/2.0, away_legend_loc[0]+cell_width*legend_scale/2.0, away_legend_loc[0]+cell_width*legend_scale/2.0, away_legend_loc[0]-cell_width*legend_scale/2.0), (away_legend_loc[1]-cell_height*legend_scale/2.0, away_legend_loc[1]+cell_height*legend_scale/2.0, away_legend_loc[1]+cell_height*legend_scale/2.0, away_legend_loc[1]-cell_height*legend_scale/2.0, away_legend_loc[1]-cell_height*legend_scale/2.0), afc)
ax.text(away_legend_loc[0]+0.75*cell_width*legend_scale, away_legend_loc[1], 'AWAY', color=otc, fontsize=gfs, fontweight='bold', verticalalignment='center')

# Time Zone Note
# ax.text(month_anchors[7][0]+3.5*cell_width, month_anchors[7][1]-8*cell_height, 'All times CDT', fontsize=dfs, horizontalalignment='center', verticalalignment='center')
ax.text(fw/2.0 + legend_x_shift*cell_width, month_anchors[legend_month][1]-6.7*cell_height + legend_add*cell_height, 'All times CDT', fontsize=dfs, horizontalalignment='center', verticalalignment='bottom')

fig.savefig(f'{year}_{team}_Schedule.pdf', bbox_inches='tight', pad_inches=0.1)
