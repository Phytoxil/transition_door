'''
Created on 5 sept. 2022

@author: Fab
'''
import schemdraw
import schemdraw.elements as elm
from schemdraw import flow
import matplotlib

if __name__ == '__main__':
    
    matplotlib.rcParams['svg.fonttype'] = 'none'
    schemdraw.use('svg')
    schemdraw.theme('solarizedl')
    
    # mermaid live ?
    # https://kroki.io/#examples
    
    with schemdraw.Drawing( file='socialVsSugar.svg' ) as d: # file='socialVsSugar.pdf'
        
        d += flow.Start().label('Start experiment')
        
        d += flow.Arrow().down(d.unit/3)
        
        d+= flow.Arrow().length(d.unit/2)
        d+= flow.Arrow().length(d.unit/2)
          
        d += flow.Start().label('Phase 1: habituation')
        
        d+=(good := flow.Box(w=2, h=1).anchor('W').label('GOOD'))
        
        d += flow.Arrow().down(d.unit/3)
        
        d += (h := flow.Decision(w=5.5, h=4, S='YES').label('Hey, wait,\nthis flowchart\nis a trap!'))
        
        d += flow.Line().down(d.unit/4)
        
        d += flow.Wire('c', k=3.5, arrow='->').to(h.E)
        
        