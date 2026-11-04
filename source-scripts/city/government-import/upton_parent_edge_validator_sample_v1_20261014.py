"""Literal existing validator seam sampler, separately callable for held context."""
import math

def parent_grid_sampler(parent):
 pg=parent['meta']['georef'];w=parent['w'];h=parent['h']
 def sample(x,z):
  c=(x+834500-pg['bE'])/pg['aE'];r=(816500-z-pg['bN'])/pg['aN'];i=max(0,min(w-2,math.floor(c)));j=max(0,min(h-2,math.floor(r)));u=c-i;v=r-j
  def at(k):
   rendered=parent.get('renderedElev',[]);a=rendered[k] if rendered else None
   return a if a is not None else max(1.2,parent['elev'][k]) if parent['elev'][k]>0 else -4
  a=at(j*w+i);b=at(j*w+i+1);d=at((j+1)*w+i);e=at((j+1)*w+i+1)
  return a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
 return sample
