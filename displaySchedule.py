from astropy.io import ascii
from astropy.table import Table, Column, Row
import datetime
import json
import matplotlib.pyplot as plt 

# =============================================================================
# USER VARIABLES
# =============================================================================

# Things that can feasibly be changed
fn = '2025RoyalsSchedule.csv'
start = 33
asg = '15/07/2025'

year = '2025'
team = 'Royals'

hfc = 'xkcd:royal blue' # Home Fill Colour
htc = 'xkcd:white' # Home Text Colour

afc = 'xkcd:sky blue' # Away Fill Colour
atc = 'xkcd:white' # Away Text Colour

ofc = 'xkcd:light grey' # Off Day Fill Colour
otc = 'xkcd:navy blue' # Off Day Text Colour

asg_fill = 'xkcd:scarlet' # ASG font colour
asg_font = 'xkcd:navy blue' # ASG fill colour
asg_location = 'Atlanta'

tbc = 'xkcd:goldenrod' # Ticket Box Colour

weekstart = 6 # Week starts on Sunday = 6, Monday = 0

legend_month = 7
legend_scale = 0.75

hour_format = '12'
ampm = False

highlight_file = ''#'2025_tickets.txt'

rows = 3
columns = 2

# Scaling parameters & things that should not be changed once everything looks good

fh = 11 # Ideal figure height
fw = 8.5 # Ideal figure width
rescale = 1.25 # Rescale you have to do becasue python won't do the figure size as-defined for annoying reasons

v_margin = 0.1 # Vertical Margin
h_margin = 0.1 # Horizontal Margin

# Even though the nubmer of columns is not used for the actual plotting, it's important here to set the cell size
cell_width = (fw - 2*h_margin) / (7*columns + 0.5*(columns-1)) # Each month is seven days wide, plus half a day's width between the months
cell_height = (cell_width * 2) / 2.5 #3.0

gfs = cell_height*25 #fw - h_margin)*1.3 # Game font size
dfs = 0.5*gfs # Date font size
mfs = 2*gfs # Month font size
hfs = min([fw*3, fh*4])# Header font size

header_add = v_margin + hfs/72

spare_height = fh - v_margin*2 - hfs/72 - (cell_height * (rows*6)) # Six weeks to a month, plus 1.5 between each row. It simplifies to r*7 - 1 = 6r + 1.5*(r-1)

month_add = spare_height*0.4
legend_add = spare_height*0.35 # Yes, these should sum to unity, but that doesn't work for some reason


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
    
def reformatMLBSchedule(fn, team, asg, start, hour_format, ampm, highlights=None):
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

ascii_sched = reformatMLBSchedule('2025RoyalsSchedule.csv', 'Royals', '15/07/2025', start, hour_format, ampm, highlights=highlights)

nickname_to_abbreviation_dict = json.load(open('nickname_to_abbreviation_traditional.json'))

# =============================================================================
# Make Calendar Schedule
# =============================================================================
months = {3:'March/April', 5:'May', 6:'June', 7:'July', 8:'August', 9:'September'}
weekdays = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}


fig = plt.figure()
fig.set_size_inches(h=fh*rescale, w=fw*rescale)
ax = fig.add_subplot(111)
ax.set_xlim(0, fw)
ax.set_ylim(-fh, 0)
ax.set_aspect('equal')
ax.set_axis_off()

#cell_height = 2
#cell_width = 3
# Set the cell height and width based off the figure size

# Header
ax.text(fw*0.5, -v_margin, f'{year} {team} Schedule'.upper(), fontsize=hfs, color=otc, horizontalalignment='center', verticalalignment='top', fontweight='bold')

column = 0
row = cell_height

# Define the anchor points for each month
#month_anchors = {3: [h_margin, v_margin - header_add - month_add], 4: [h_margin, v_margin - header_add - month_add - 1*cell_height], 5: [h_margin, v_margin - header_add - month_add*2 - 6*cell_height], 6: [h_margin+7.5*cell_width, v_margin - header_add - month_add], 7: [h_margin+7.5*cell_width, v_margin - header_add - month_add*2 - 6*cell_height], 8: [h_margin+15*cell_width, v_margin - header_add - month_add], 9: [h_margin+15*cell_width, v_margin - header_add - month_add*2 - 6*cell_height]}
month_anchors = {3: [h_margin, v_margin - header_add - month_add], 4: [h_margin, v_margin - header_add - month_add - 1*cell_height]} # This will always be true
for month_number in range(5, 10):
    monthcol = (month_number - 4)//rows
    monthrow = (month_number - 4)%rows
    # Note that the number of columns is actually not used here.
    # This allows an arbitrary number of months, though it's unlikely to ever not be six.
    # It will run down a column until it hits the maximum number of rows, or runs out of months
    month_anchors[month_number] = [h_margin + (7.5*cell_width)*monthcol, v_margin - header_add - month_add*(1 + monthrow) - (6*cell_height)*monthrow]

current_month = 3
# Month and week headers
for month_ordinal in months.keys():
    ax.text(month_anchors[month_ordinal][0]+cell_width*3.5, month_anchors[month_ordinal][1]+1*cell_height, months[month_ordinal].upper(), fontsize=mfs, color=otc, horizontalalignment='center', verticalalignment='center', fontweight='bold')
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

home_legend_loc = [fw/2.0-1.5*cell_width*legend_scale, month_anchors[legend_month][1]-5*cell_height - legend_add*0.5]
away_legend_loc = [fw/2.0+1.5*cell_width*legend_scale, month_anchors[legend_month][1]-5*cell_height - legend_add*0.5]

ax.fill((home_legend_loc[0]-cell_width*legend_scale/2.0, home_legend_loc[0]-cell_width*legend_scale/2.0, home_legend_loc[0]+cell_width*legend_scale/2.0, home_legend_loc[0]+cell_width*legend_scale/2.0, home_legend_loc[0]-cell_width*legend_scale/2.0), (home_legend_loc[1]-cell_height*legend_scale/2.0, home_legend_loc[1]+cell_height*legend_scale/2.0, home_legend_loc[1]+cell_height*legend_scale/2.0, home_legend_loc[1]-cell_height*legend_scale/2.0, home_legend_loc[1]-cell_height*legend_scale/2.0), hfc)
ax.text(home_legend_loc[0]+0.75*cell_width*legend_scale, home_legend_loc[1], 'HOME', color=otc, fontsize=gfs, fontweight='bold', verticalalignment='center')

ax.fill((away_legend_loc[0]-cell_width*legend_scale/2.0, away_legend_loc[0]-cell_width*legend_scale/2.0, away_legend_loc[0]+cell_width*legend_scale/2.0, away_legend_loc[0]+cell_width*legend_scale/2.0, away_legend_loc[0]-cell_width*legend_scale/2.0), (away_legend_loc[1]-cell_height*legend_scale/2.0, away_legend_loc[1]+cell_height*legend_scale/2.0, away_legend_loc[1]+cell_height*legend_scale/2.0, away_legend_loc[1]-cell_height*legend_scale/2.0, away_legend_loc[1]-cell_height*legend_scale/2.0), afc)
ax.text(away_legend_loc[0]+0.75*cell_width*legend_scale, away_legend_loc[1], 'AWAY', color=otc, fontsize=gfs, fontweight='bold', verticalalignment='center')

# Time Zone Note
# ax.text(month_anchors[7][0]+3.5*cell_width, month_anchors[7][1]-8*cell_height, 'All times CDT', fontsize=dfs, horizontalalignment='center', verticalalignment='center')
ax.text(fw/2.0, month_anchors[legend_month][1]-5*cell_height - legend_add, 'All times CDT', fontsize=dfs, horizontalalignment='center', verticalalignment='bottom')

fig.savefig(f'{year}_{team}_Schedule.pdf', bbox_inches='tight', pad_inches=0.1)
