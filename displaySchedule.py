from astropy.io import ascii
from astropy.table import Table, Column, Row
import datetime
import json
import matplotlib.pyplot as plt

# =============================================================================
# USER VARIABLES
# =============================================================================

year = '2025'
team = 'Royals'

hfc = 'xkcd:royal blue' # Home Fill Colour
htc = 'xkcd:white' # Home Text Colour

afc = 'xkcd:sky blue' # Away Fill Colour
atc = 'xkcd:white' # Away Text Colour

ofc = 'xkcd:light grey' # Off Day Fill Colour
otc = 'xkcd:navy blue' # Off Day Text Colour

tbc = 'xkcd:goldenrod' # Ticket Box Colour

# gfs = 6 # Game font size
fh = 8.5 * 1.2 # Figure height
fw = 7 * 8.5/5 * 1.2 # Figure width
gfs = fh / 1.25 # Game font size
dfs = 0.5*gfs # Date font size
mfs = 2*gfs # Month font size

weekstart = 6 # Week starts on Sunday == 6, Monday == 0

# =============================================================================
# Read in and format text file
# =============================================================================
fn = '2025RoyalsSchedule.csv'
start = 192
asg = '15/07/2025'

highlights = open('2025_tickets.txt').readlines()
for i in range(len(highlights)):
    highlights[i] = highlights[i][:-1]
    
def reformatMLBSchedule(fn, team, asg, start, highlights=None):
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
            if not sched_date['START TIME'].mask:
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
        
        asciischedule.add_row([i, gamedatetime.strftime('%d/%m/%Y'), opp, loc, gamedatetime.strftime('%H:%M'), highlight])
    
    return asciischedule

# =============================================================================
# SET IMPORTANT DATES AND LOAD ABBREVIATIONS
# =============================================================================

ascii_sched = reformatMLBSchedule('2025RoyalsSchedule.csv', 'Royals', '15/07/2025', 192, highlights=highlights)

nickname_to_abbreviation_dict = json.load(open('nickname_to_abbreviation_traditional.json'))

# =============================================================================
# Make Calendar Schedule
# =============================================================================
months = {3:'March/April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September'}
weekdays = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}


fig = plt.figure()
fig.set_size_inches(h=fh, w=fw)
ax = fig.add_subplot(111)
ax.set_aspect('equal')
ax.set_axis_off()

cell_height = 2
cell_width = 3

column = 0
row = 1

month_anchors = {3: [0, 0], 4: [0, -1*cell_height], 5: [0, -9*cell_height], 6: [8*cell_width, 0], 7: [8*cell_width, -9*cell_height], 8: [16*cell_width, 0], 9: [16*cell_width, -9*cell_height]}
current_month = 3

ax.text(month_anchors[6][0]+cell_width*3.5, month_anchors[6][1]+4*cell_height, f'{year} {team} Schedule'.upper(), fontsize=mfs*2, color=otc, horizontalalignment='center', verticalalignment='center', fontweight='bold')

for month_ordinal in months.keys():
    ax.text(month_anchors[month_ordinal][0]+cell_width*3.5, month_anchors[month_ordinal][1]+1*cell_height, months[month_ordinal].upper(), fontsize=mfs, color=otc, horizontalalignment='center', verticalalignment='center', fontweight='bold')
    for day in weekdays.keys():
        ax.text(month_anchors[month_ordinal][0] + (day - weekstart)%7*cell_width, month_anchors[month_ordinal][1]+0.25*cell_height, weekdays[day].upper(), color=otc, fontsize=dfs, horizontalalignment='center', verticalalignment='center')

ascii_sched.sort('ordinal_date') # It should already be, but just in case

for entry in ascii_sched.iterrows():
    date = datetime.date.fromordinal(entry[0])
    week_ordinal = (date.weekday() - weekstart)%7
    
    if entry[3] == 'H':
        fillcolour = hfc
        textcolour = htc
        opp = nickname_to_abbreviation_dict[entry[2]]
        
    elif entry[3] == 'A':
        fillcolour = afc
        textcolour = atc
        opp = nickname_to_abbreviation_dict[entry[2]]
        
    else:
        fillcolour = ofc
        textcolour = otc
        
        if entry[2] == 'ALL-STAR GAME':
            opp = 'ALL-STAR BREAK'
        else:
            opp = ''
    
    if entry[5] == True:
        ec = tbc
        zo = 10
    else:
        ec = 'w'
        zo = 2
    
    if date.month != current_month:
        row = 1
        current_month = date.month
    
    if week_ordinal == 0:
        row += cell_height
    
    x_centre = month_anchors[date.month][0] + week_ordinal*cell_width
    y_centre = month_anchors[date.month][1] - row
    
    ax.plot([x_centre-cell_width/2.0, x_centre-cell_width/2.0], [y_centre-cell_height/2.0, y_centre+cell_height/2.0], c=ec, lw=gfs/6, zorder=zo)
    ax.plot([x_centre+cell_width/2.0, x_centre+cell_width/2.0], [y_centre-cell_height/2.0, y_centre+cell_height/2.0], c=ec, lw=gfs/6, zorder=zo)
    ax.plot([x_centre-cell_width/2.0, x_centre+cell_width/2.0], [y_centre-cell_height/2.0, y_centre-cell_height/2.0], c=ec, lw=gfs/6, zorder=zo)
    ax.plot([x_centre-cell_width/2.0, x_centre+cell_width/2.0], [y_centre+cell_height/2.0, y_centre+cell_height/2.0], c=ec, lw=gfs/6, zorder=zo)
    
    ax.fill((x_centre-cell_width/2.0, x_centre-cell_width/2.0, x_centre+cell_width/2.0, x_centre+cell_width/2.0, x_centre-cell_width/2.0), (y_centre-cell_height/2.0, y_centre+cell_height/2.0, y_centre+cell_height/2.0, y_centre-cell_height/2.0, y_centre-cell_height/2.0), fillcolour)
    
    ax.text(x_centre-cell_width/2.0+cell_width*0.06, y_centre+cell_height/2.0-cell_height*0.1, date.day, color=textcolour, fontsize=dfs, verticalalignment='top')
    ax.text(x_centre, y_centre, opp, fontsize=gfs, color=textcolour, fontweight='bold', horizontalalignment='center', verticalalignment='center')

home_legend_loc = [month_anchors[7][0]+2*cell_width, month_anchors[7][1]-7*cell_height]
away_legend_loc = [month_anchors[7][0]+5*cell_width, month_anchors[7][1]-7*cell_height]

ax.fill((home_legend_loc[0]-cell_width/2.0, home_legend_loc[0]-cell_width/2.0, home_legend_loc[0]+cell_width/2.0, home_legend_loc[0]+cell_width/2.0, home_legend_loc[0]-cell_width/2.0), (home_legend_loc[1]-cell_height/2.0, home_legend_loc[1]+cell_height/2.0, home_legend_loc[1]+cell_height/2.0, home_legend_loc[1]-cell_height/2.0, home_legend_loc[1]-cell_height/2.0), hfc)
ax.text(home_legend_loc[0]+0.75*cell_width, home_legend_loc[1], 'HOME', color=otc, fontsize=gfs, fontweight='bold', verticalalignment='center')

ax.fill((away_legend_loc[0]-cell_width/2.0, away_legend_loc[0]-cell_width/2.0, away_legend_loc[0]+cell_width/2.0, away_legend_loc[0]+cell_width/2.0, away_legend_loc[0]-cell_width/2.0), (away_legend_loc[1]-cell_height/2.0, away_legend_loc[1]+cell_height/2.0, away_legend_loc[1]+cell_height/2.0, away_legend_loc[1]-cell_height/2.0, away_legend_loc[1]-cell_height/2.0), afc)
ax.text(away_legend_loc[0]+0.75*cell_width, away_legend_loc[1], 'AWAY', color=otc, fontsize=gfs, fontweight='bold', verticalalignment='center')

ax.text(month_anchors[7][0]+3.5*cell_width, month_anchors[7][1]-8*cell_height, 'All times CDT', fontsize=dfs, horizontalalignment='center', verticalalignment='center')

fig.savefig(f'{year}_{team}_Schedule.pdf', bbox_inches='tight', pad_inches=0.1)
