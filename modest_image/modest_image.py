import matplotlib.image as mi


class ModestImage(mi.AxesImage):
    """
    Computationally modest image class.

    ModestImage is an extension of the Matplotlib AxesImage class
    better suited for the interactive display of larger images. Before
    drawing, ModestImage resamples the data array based on the screen
    resolution and view window. This has very little affect on the
    appearance of the image, but can substantially cut down on
    computation since calculations of unresolved or clipped pixels
    are skipped.

    The interface of ModestImage is the same as AxesImage. However, it
    does not currently support setting the 'extent' property. There
    may also be weird coordinate warping operations for images that
    I'm not aware of. Don't expect those to work either.
    """
    def __init__(self, *args, **kwargs):
        self._full_res = None
        self._sx, self._sy = None, None
        self._bounds = (None, None, None, None)
        super(ModestImage, self).__init__(*args, **kwargs)

    def set_data(self, A):
        super(ModestImage, self).set_data(A)
        self._full_res = A
        self._sx, self._sy = None, None  # force redraw

    def _scale_to_res(self):
        """ Change self._A and _extent to render an image whose
        resolution is matched to the eventual rendering."""

        ax = self.axes
        ext = ax.transAxes.transform([1, 1]) - ax.transAxes.transform([0, 0])
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        dx, dy = xlim[1] - xlim[0], ylim[1] - ylim[0]

        y0 = max(0, ylim[0] - dy)
        y1 = min(self._full_res.shape[0], ylim[1] + dy)
        x0 = max(0, xlim[0] - dx)
        x1 = min(self._full_res.shape[1], xlim[1] + dx)
        y0, y1, x0, x1 = map(int, [y0, y1, x0, x1])

        sy = max(1, min((y1 - y0) / 5., dy / ext[1]))
        sx = max(1, min((x1 - x0) / 5., dx / ext[0]))

        # have we already calculated what we need?
        if sx == self._sx and sy == self._sy and \
            x0 >= self._bounds[0] and x1 <= self._bounds[1] and \
            y0 >= self._bounds[2] and y1 <= self._bounds[3]:
            return

        self._A = self._full_res[y0:y1:sy, x0:x1:sx]
        x1 = x0 + self._A.shape[1]
        y1 = y0 + self._A.shape[0]

        self.set_extent([x0 - .5, x1 - .5, y0 - .5, y1 - .5])
        self._sx = sx
        self._sy = sy
        self._bounds = (x0, x1, y0, y1)
        self.changed()

    def draw(self, renderer, *args, **kwargs):
        self._scale_to_res()
        super(ModestImage, self).draw(renderer, *args, **kwargs)


def main():
    from time import time
    import matplotlib.pyplot as plt
    import numpy as np
    x, y = np.mgrid[0:2000, 0:2000]
    data = np.sin(x / 10.) * np.cos(y / 30.)

    f = plt.figure()
    ax = f.add_subplot(111)

    #try switching between
    artist = ModestImage(ax, data=data)
    #artist = mi.AxesImage(ax, data=data)

    ax.set_aspect('equal')
    artist.norm.vmin = -1
    artist.norm.vmax = 1

    ax.add_artist(artist)
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 1000)

    t0 = time()
    plt.gcf().canvas.draw()
    t1 = time()

    print "Draw time for %s: %0.1f ms" % (artist.__class__.__name__,
                                          (t1 - t0) * 1000)

    plt.show()


if __name__ == "__main__":
    main()
