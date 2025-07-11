"""
Functions for comparing the optical distributions of a madx model
and a Transport model.

Functions for plotting the individual optical functions, and an
eighth, helper function ''compare_all_optics``, to plot display all
seven in one go.
"""
import datetime as _datetime
import matplotlib.pyplot as _plt
from matplotlib.backends.backend_pdf import PdfPages as _PdfPages

from ._CompareCommon import _LoadTfsInfput
from .. import Plot as _Plot

from pytransport import Reader as _Reader

_BETA = [("BETX", "Beta_x", r'$\beta_{x}$'),
         ("BETY", "Beta_y", r'$\beta_{y}$')]

_ALPHA = [("ALFX", "Alpha_x", r"$\alpha_{x}$"),
          ("ALFY", "Alpha_y", r"$\alpha_{y}$")]

_DISP = [("DXBETA", "Disp_x", r"$D_{x}$ / $\beta$"),
         ("DYBETA", "Disp_y", r"$D_{y}$ / $\beta$")]

_DISP_P = [("DPXBETA", "Disp_xp", r"$D_{p_{x}}$"),
           ("DPYBETA", "Disp_yp", r"$D_{p_{y}}$")]

_SIGMA = [("SIGMAX", "Sigma_x", r"$\sigma_{x}$"),
          ("SIGMAY", "Sigma_y", r"$\sigma_{y}$")]

_SIGMA_P = [("SIGMAXP", "Sigma_xp", r"$\sigma_{xp}$"),
            ("SIGMAYP", "Sigma_yp", r"$\sigma_{yp}$")]

# use closure to avoid tonnes of boilerplate code as happened with
# MadxBdsimComparison.py
def _make_plotter(plot_info_tuples, x_label, y_label, title):
    def f_out(first, second, first_name=None, second_name=None, **kwargs):
        """first and second should be tfs files."""
        first, first_name = _LoadTfsInfput(first, first_name)
        second = _Reader.GetOptics(second)

        plot = _plt.figure(title, figsize=(9,5), **kwargs)
        # Loop over the variables in plot_info_tuples and draw the plots.
        for madxVar, transVar, legend_name in plot_info_tuples:
            _plt.plot(first.GetColumn('S'), first.GetColumn(madxVar),
                      label="{}: {}".format(legend_name, first_name), **kwargs)
            _plt.plot(second.GetColumn('S'), second.GetColumn(transVar),
                      label="{}: {}".format(legend_name, second_name), **kwargs)

        # Set axis labels and draw legend
        axes = _plt.gcf().gca()
        axes.set_ylabel(y_label)
        axes.set_xlabel(x_label)
        axes.legend(loc='best')

        _Plot.AddMachineLatticeToFigure(plot, first)
        _plt.show(block=False)
        return plot
    return f_out

PlotBeta   = _make_plotter(_BETA,    "S / m", r"$\beta_{x,y}$ / m",      "Beta")
PlotAlpha  = _make_plotter(_ALPHA,   "S / m", r"$\alpha_{x,y}$ / m",     "Alpha")
PlotDisp   = _make_plotter(_DISP,    "S / m", r"$D_{x,y} / m$",          "Dispersion")
PlotDispP  = _make_plotter(_DISP_P,  "S / m", r"$D_{p_{x},p_{y}}$ / m",  "Momentum_Dispersion")
PlotSigma  = _make_plotter(_SIGMA,   "S / m", r"$\sigma_{x,y}$ / m",     "Sigma")
PlotSigmaP = _make_plotter(_SIGMA_P, "S / m", r"$\sigma_{xp,yp}$ / rad", "SigmaP")
#PlotMean   = _make_plotter(_MEAN,    "S / m", r"$\bar{x}, \bar{y}$ / m", "Mean")


def MADXVsTRANSPORT(first, second, first_name=None,
               second_name=None, saveAll=True, 
               outputFileName=None, **kwargs):
    """
    Display all the optical function plots for the two input optics files.
    """
    figures = [
    PlotBeta(first, second, first_name=first_name,
             second_name=second_name, **kwargs),
    PlotAlpha(first, second, first_name=first_name,
              second_name=second_name, **kwargs),
    PlotDisp(first, second, first_name=first_name,
             second_name=second_name, **kwargs),
    PlotDispP(first, second, first_name=first_name,
              second_name=second_name, **kwargs),
    PlotSigma(first, second, first_name=first_name,
              second_name=second_name, **kwargs),
    PlotSigmaP(first, second, first_name=first_name,
               second_name=second_name, **kwargs)
    ]

    if saveAll:
        if outputFileName is not None:
            output_filename = outputFileName
        else:
            output_filename = "optics-report.pdf"
        with _PdfPages(output_filename) as pdf:
            for figure in figures:
                pdf.savefig(figure)
            d = pdf.infodict()
            d['Title'] = "{} VS {} Optical Comparison".format(first_name, second_name)
            d['CreationDate'] = _datetime.datetime.today()
        print("Written ", output_filename)
