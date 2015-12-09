.. _planar_imaging:

===================================
Planar Imaging module documentation
===================================

Overview
--------

.. automodule:: pylinac.planar_imaging
    :no-members:

Running the Leeds Demo
----------------------

To run the Leeds TOR demo, create a script or start an interpreter session and input::

    from pylinac import LeedsTOR

    LeedsTOR.run_demo()

A figure showing the phantom, low contrast plot, and RMTF will be generated:

.. image:: images/leeds_analysis.png

Image Acquisition
-----------------

You can acquire the images any way you like. Just ensure that the phantom is not touching a field edge. It
is also recommended by the manufacturer to rotate the phantom to a non-cardinal angle so that pixel aliasing does not occur for the
high-contrast line pairs.

Typical Use
-----------

The VMAT QA analysis follows what is specified in the Varian RapidArc QA tests and assumes your tests will run the exact same way.
Import the class::

    from pylinac import LeedsTOR

The minimum needed to get going is to:

* **Load image** -- Load the planar image as you would any other class: by passing the path directly to the constructor::

      leeds = LeedsTOR('my/leeds.dcm')

  Alternatively, a URL can be passed::

      leeds = LeedsTOR.from_url('http://myserver.com/leeds')

  You may also use the demo image::

      leeds = LeedsTOR.from_demo_image()

* **Analyze the images** -- Analyze the image using the :meth:`~pylinac.planar_imaging.LeedsTOR.analyze` method. The
  low and high contrast thresholds can be specified::

      leeds.analyze(low_contrast_threshold=0.01, hi_contrast_threshold=0.5)

* **View the results** -- The results of analysis can be viewed with the :meth:`~pylinac.planar_imaging.LeedsTOR.plot_analyzed_image`
  method. Note that each subimage can be turned on or off.::

      # don't show the low contrast plot
      leeds.plot_analyzed_image(lowcontrast=False)

  .. image:: images/leeds_no_lc.png

  The figure can also be saved::

      leeds.save_analyzed_image('myprofile.png')

Algorithm
---------

Leeds phantom analysis is straightforward: find the phantom in the image, then sample ROIs at the appropriate
locations.

The algorithm works like such:

**Allowances**

* The images can be acquired at any SID.
* The images can be acquired with any EPID (aS500, aS1000, aS1200).
* The phantom can be at any angle.
* The phantom can be flipped either way.

**Restrictions**

    .. warning:: Analysis can fail or give unreliable results if any Restriction is violated.

* The images must be acquired with the EPID.
* The phantom must not be touching any image edges.

**Pre-Analysis**

* **Determine phantom location** -- The Leeds phantom is found by searching for the circular metal ring
  near the edge of the phantom. The image is converted to binary based on an initial threshold. If a ring-like
  structure is found then the center of the ring is determined as the phantom center. If the ring structure
  was not found the image is iteratively converted to binary again with a slightly higher threshold until the
  structure is found.
* **Determine phantom angle** -- To find the rotational angle of the phantom, a similar process is employed.
  The original image is converted to binary and the lead square is iteratively searched for by looking for an
  appropriately-sized and solid square ROI. Once found, the angle between the phantom center and lead square
  provides the baseline angle.
* **Determine rotation direction** -- The phantom might be placed upside down. To keep analysis consistent,
  a circular profile is sampled at the radius of the low contrast ROIs starting at the lead square. Peaks are
  searched for on each semicircle. The side with the most peaks is the side with the higher contrast ROIs.

**Analysis**

* **Calculate low contrast** -- Because the phantom center and angle are known, the angles to the ROIs can also
  be known. For each contrast ROI, both it and a background ROI are sampled. From here, the contrast can be known:
  :math:`Contrast_{ROI} = \frac{ROI_{val} - ROI_{background}}{ROI_{val} + ROI_{background}}`.
* **Calculate high contrast** -- Again, because the phantom position and angle are known, offsets are applied
  to sample the high contrast line pair regions. For each sample, the relative MTF is calculated:
  :math:`MTF_{ROI} = \frac{ROI_{max} - ROI_{min}}{ROI_{max} + ROI_{min}}`.

**Post-Analysis**

* **Determine passing low and high contrast ROIs** -- For each low and high contrast region, the determined
  value is compared to the threshold. The plot colors correspond to the pass/fail status.

API Documentation
-----------------

.. autoclass:: pylinac.planar_imaging.LeedsTOR