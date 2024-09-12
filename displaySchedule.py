import datetime
import json
import matplotlib.pyplot as plt


fig = plt.figure()
fig.set_size_inches(h=5, w=7)
ax = fig.add_subplot(111)
ax.set_aspect('equal')
ax.set_axis_off()

cell_height = 2
cell_width = 3

column = 1
row = 0
current_month = 3
for i in range(openingday, closingday+1, 1):
    date = datetime.date.fromordinal(i)
    
    sched_date = schedule2025[schedule2025['START DATE'] == date.strftime('%m/%d/%y')]
    
    if len(sched_date) == 1:
        matchup = sched_date[0]['SUBJECT'].split(' - ')[0]
        awayteam, hometeam = matchup.split(' at ')
        
        if hometeam == 'Royals':
            fillcolour = 'xkcd:royal blue'
            datecolour = 'xkcd:white'
            opp = nickname_to_abbreviation_dict[awayteam]
        else:
            fillcolour = 'xkcd:sky blue'
            datecolour = 'xkcd:black'
            opp = nickname_to_abbreviation_dict[hometeam]
    else:
        fillcolour = 'xkcd:light grey'
        datecolour='xkcd:black'
        opp = ''
    
    if date.weekday() == 0:
        row -= cell_height
    
    if date.month != current_month:
        if date.month != 4:
            row -= cell_height*4
        if date.month in (6, 8):
            column += cell_width*8
            row = 0
        current_month = date.month
    
    x_centre = column + date.weekday()*cell_width
    y_centre = row
    
    ax.plot([x_centre-cell_width/2.0, x_centre-cell_width/2.0], [y_centre-cell_height/2.0, y_centre+cell_height/2.0], c='w', lw=1)
    ax.plot([x_centre+cell_width/2.0, x_centre+cell_width/2.0], [y_centre-cell_height/2.0, y_centre+cell_height/2.0], c='w', lw=1)
    ax.plot([x_centre-cell_width/2.0, x_centre+cell_width/2.0], [y_centre-cell_height/2.0, y_centre-cell_height/2.0], c='w', lw=1)
    ax.plot([x_centre-cell_width/2.0, x_centre+cell_width/2.0], [y_centre+cell_height/2.0, y_centre+cell_height/2.0], c='w', lw=1)
    
    ax.fill((x_centre-cell_width/2.0, x_centre-cell_width/2.0, x_centre+cell_width/2.0, x_centre+cell_width/2.0, x_centre-cell_width/2.0), (y_centre-cell_height/2.0, y_centre+cell_height/2.0, y_centre+cell_height/2.0, y_centre-cell_height/2.0, y_centre-cell_height/2.0), fillcolour)
    
    ax.text(x_centre-cell_width/2.0+cell_width*0.06, y_centre+cell_height/2.0-cell_height*0.1, date.day, color=datecolour, fontsize=2, verticalalignment='top')
    ax.text(x_centre, y_centre, opp, fontsize=4, color='xkcd:white', fontweight='bold', horizontalalignment='center', verticalalignment='center')
    
fig.savefig('2025_EarlyBird_Schedule.pdf')
