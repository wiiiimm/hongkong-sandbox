"""Unshaded scientific display; no geometry or authored GPU material changes."""
from aqua_saved_context_display_v1_20261014 import plot_xyz

def solid_collection(tri,color,alpha=1.,edge='none',width=.1):
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    return Poly3DCollection(plot_xyz(tri),facecolors=color,edgecolors=edge,linewidths=width,shade=False,alpha=alpha)
