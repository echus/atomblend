# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   analysis/voxelisation.py
# Date:   2014-11-05
# Author: Clara Tan
#
# Description:
# Voxelisation function
# =============================================================================

import numpy as np

def generate(coords, bin=1):
    """
    Voxelise the data in XYZ and return the volume in each voxel
    as a 3D matrix of Ni x Nj x Nk.

    Input - 'coords': The pointcloud as [x1 y1 z1; x2 y2 z2; ...] where each row is
    the xyz coordinate of each point
          - 'bin'   : Bin (division) size in nanometres. Must be greater than
          or equal to the smallest measurable division of XYZ (ie: one atom
          cannot be in two voxels)

    Output - 'threedee': Voxelized pointcloud as a 3D matrix, tallying the number of
    points per voxel (bin) across the volume of the pointcloud
    """

    if coords.shape[1] != 3:
        raise ValueError("Positions not entered as columns X, Y, Z.")

    # Calculate min, max and range of XYZ
    min_ = np.empty(3)
    max_ = np.empty(3)
    range_ = np.empty(3)
    for i in np.arange(3):
        min_[i] = np.nanmin(coords[:,i])
        max_[i] = np.nanmax(coords[:,i])
        range_[i] = max_[i] - min_[i]


    # Calculate the number of voxels in IJK via rounding range in XYZ up
    # to an integer value
    N = np.zeros(3)
    for x in np.arange(3):
        N[x] = (range_[x]//bin) + 1 # IJK


    # Create the voxel volume (3D matrix)
    voxelarray = np.zeros((N[1], N[2], N[0]))
    voxelID = np.zeros(3) #per record
    voxelIDarray = np.empty([coords.shape[0], 3])

    # Per record: iterate through all coord values and calculate their
    # appropriate voxel bin
    # Store the voxel's index in voxelID
    # At that voxelID, increase the count by 1 in the 3D matrix
    # Return completed voxel volume
    for record in np.arange(coords.shape[0]):
        for xyz in np.arange(3):
            voxelID[xyz] =(( coords[record, xyz] - min_[xyz]) // bin) #brackets important
        voxelarray[voxelID[1], voxelID[2], voxelID[0]] = voxelarray[voxelID[1], voxelID[2], voxelID[0]] + 1 #add 1 to count at this index

    return voxelarray
