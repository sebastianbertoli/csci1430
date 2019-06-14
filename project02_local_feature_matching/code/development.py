import numpy as np
from scipy.spatial.distance import cdist

def get_idx_2smallest_dist(distances):
    """Given a distance matrix it returns the index of the k
    smallest distances.

    Parameters
    ----------

    distances: 2d-array distance matrix

    Returns
    -------
    
    d1_ix, d2_ix: Tuple.
        For eact row of the distance matrix it returns the index of the smallest
        and second smallest distance.

    """
    n_rows = distances.shape[0]
    idxs = np.argsort(distances, axis=1)[:, :2]
    d1_ix = [np.arange(n_rows), idxs[:,0]]
    d2_ix = [np.arange(n_rows), idxs[:,1]]
    return d1_ix, d2_ix

def match_features(im1_features, im2_features):
    """ Returns the index of the common image features as well as the 
    confidence of a correct match.
    
    Parameters
    ----------
    
    im1_features: array, features of image 1.
    
    im2_features: array, features of image 2.
    
    Returns
    -------
    
    matches: array
        First column = matches for image 1.
        Second column = matches for image 2.
    
    confidences: list, confidence for each match identified. 
        We define it as:

            confidence = 1 - NNDR
        
        where:

        NDDR = \frac{d_1}{d_2} = \frac{||D_A - D_B||}{||D_A - D_C||}

        See Equation 4.18 in Section 4.1.3 of Szeliski.
    """
    distances = cdist(im1_features, im2_features, metric="euclidean")
    d1_ix, d2_ix = get_idx_2smallest_dist(distances)
    nddr = distances[d1_ix] / distances[d2_ix]

    matches = np.stack((d1_ix[0], d1_ix[1]), axis=1)
    confidences = 1 - nddr
    
    return matches, confidences

def get_features(image, x, y, feature_width):
    '''
    Returns a set of feature descriptors for a given set of interest points.

    
    Parameters
    ----------

    image: a grayscale or color image (your choice depending on your 
        implementation)
    x: np array of x coordinates of interest points
    y: np array of y coordinates of interest points
    feature_width: in pixels, is the local feature width. You can assume
        that feature_width will be a multiple of 4 (i.e. every cell of your
        local SIFT-like feature will have an integer width and height).

    Returns
    -------

    features: np array of computed features. It should be of size
            [len(x) * feature dimensionality] (for standard SIFT feature
            dimensionality is 128)

    '''
    if feature_width % 4 != 0:
        raise ValueError("feature_width must be a multiple of 4.")
    x = np.round(x).astype(int).flatten()
    y = np.round(y).astype(int).flatten()
    offset = feature_width // 2
    descriptors = list()
    n_bins = 8
    
    # compute gradients, magnitudes, angles
    gradients = np.array(np.gradient(image))
    magnitudes = np.linalg.norm(gradients, axis=0)
    angles = np.angle(np.arctan2(gradients[0], gradients[1]), deg=True)
    
    # Loop through keypoints
    for xi, yi in zip(x,y):
        #crop_image = image[yi-offset+1:yi+offset+1, xi-offset+1:xi+offset+1]
        crop_magnitudes = magnitudes[yi-offset+1:yi+offset+1, xi-offset+1:xi+offset+1]
        crop_angles = angles[yi-offset+1:yi+offset+1, xi-offset+1:xi+offset+1]
        if crop_magnitudes.shape != (feature_width, feature_width):
            # Crop does not satisfy size constraint, skip keypoint.
            print("skip")
            continue

        # Create SIFT descriptor
        patches_magnitudes = np.array(np.hsplit(np.array(np.hsplit(crop_magnitudes, 4)).reshape(4,-1),4)).reshape(-1,feature_width)
        patches_angles = np.array(np.hsplit(np.array(np.hsplit(crop_angles, 4)).reshape(4,-1),4)).reshape(-1,feature_width)
        feature_vector = list()
        for patch_i in range(patches_magnitudes.shape[0]):
            bins = np.digitize(patches_angles[patch_i], np.arange(0,360,360 // n_bins))
            bin_vector = np.zeros(n_bins)
            for bin_i in range(0, n_bins):
                mask = np.array(bins == bin_i).flatten()
                bin_vector[bin_i] = np.sum(patches_magnitudes[patch_i].flatten()[mask])
            bin_vector = bin_vector / np.sum(bin_vector)
            feature_vector.append(bin_vector)
        descriptors.append(np.array(feature_vector).flatten())
    return np.array(descriptors)