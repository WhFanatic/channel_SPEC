#!/work1/cuigx2_work/whn/anaconda_install/anaconda3/bin/python

from collections import Iterable
from MyTecplot import *


class Case:
	def __init__(self, path, name="case0", color=None, style=None):

		self.path = path
		self.name = name

		self.color = color
		self.style = style

		self.plot = Tecplot()

		self.y_plus = np.loadtxt(open(self.path+'y_plus.dat'))
		self.j_probes = np.array([ int(n) for n in np.ravel(np.loadtxt(open(self.path+'j_probes.dat'))) ])
		self.Re_tau = np.loadtxt(open(self.path+'Re_tau.dat'))
		self.u_tau = np.loadtxt(open(self.path+'u_tau.dat'))
		self.delta_nu = 1.0 / self.Re_tau
		self.t_nu = self.delta_nu / self.u_tau
		self.tau_w = self.u_tau**2

	def copy(self, path=-1, name=-1, color=-1, style=-1):
		return Case(
			path = self.path if path==-1 else path,
			name = self.name if name==-1 else name,
			color = self.color if color==-1 else color,
			style = self.style if style==-1 else style	)

	def curve(self, ax, filename, n, **kwarg):
		ka = {key:kwarg[key] for key in kwarg.keys()}
		if "color" not in ka.keys(): ka["color"] = self.color
		if "linestyle" not in ka.keys() and "ls" not in ka.keys(): ka["linestyle"] = self.style
		if "linewidth" not in ka.keys() and "lw" not in ka.keys(): ka["linewidth"] = 2

		c = self.plot.curve(ax, self.path+filename, n, **ka)

	def contour(self, ax, filename, n, filled=0, **kwarg):
		ka = {key:kwarg[key] for key in kwarg.keys()}
		if "colors" not in ka.keys(): ka["colors"] = self.color
		if "linestyles" not in ka.keys(): ka["linestyles"] = self.style
		if "linewidths" not in ka.keys(): ka["linewidths"] = 1

		c = self.plot.contour(ax, self.path+filename, n, filled, **ka)


# Notes:
# Figure structure should not be adjustable outside the functions
# Adjustable variables should only be the number of curves to plot in one subplot

class Figures():
	def __init__(self,
		figure_path = "figures/",
		lambda_x_plus_lim = [16, 3500],
		lambda_z_plus_lim = [8, 350],
		y_plus_lim = [1, 200]	):

		self.figure_path = figure_path
		self.lambda_x_plus_lim = lambda_x_plus_lim
		self.lambda_z_plus_lim = lambda_z_plus_lim
		self.y_plus_lim = y_plus_lim
		self.k_x_plus_lim = list( np.array([-1, 1]) * 2*np.pi / min(self.lambda_x_plus_lim) )
		self.k_t_plus_lim = list( np.array([-1, 1]) * 15 * max(self.k_x_plus_lim) )

	def save(self, fig, figname):
		fig.tight_layout()
		fig.savefig(self.figure_path+figname+'.png', dpi=200)
		plt.close()

	##### plot #####

	def plot_MeanU(self, cases, figname='MeanU'):
		fig, ax = plt.subplots(num=figname, figsize=(4, 4))

		for case in cases: case.curve(ax, 'means_plot.dat', 1)

		ax.legend([case.name for case in cases], loc='upper left', fontsize=8, handlelength=5, frameon=False)
		ax.set_xlim(self.y_plus_lim)
		ax.set_ylim([0,20])

		self.save(fig, figname)


	def plot_FlucIntens(self, cases, figname='FlucIntens'):
		ns = (1,2,3,5)
		ylims = ([0,10], [0,1.5], [0,2.4], [0,10])

		fig, axs = plt.subplots(2, 2, sharex=True, num=figname, figsize=(6, 4))

		for ax, n, ylim in zip(np.ravel(axs), ns, ylims):

			for case in cases: case.curve(ax, 'statis_plot.dat', n)

			ax.set_xlim(self.y_plus_lim)
			ax.set_ylim(ylim)

		axs[0,1].legend([case.name for case in cases], loc='upper left', fontsize=8, handlelength=5, frameon=False)
		axs[0,0].set_xlabel('')
		axs[0,1].set_xlabel('')

		self.save(fig, figname)


	def plot_TimeSpaceSpectra(self, cases, figname='TimeSpaceSpectra'):
		ns = (1, 2, 3, 4)
		js = (1, 2, 5)
		yps = (5,15,100)
		levels = (-3, -1, 1)

		fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(6, 6))
		
		for axr, n in zip(axs, ns):	# row
			for ax, yp, j in zip(axr, yps, js):	# col

				if isinstance(cases, Iterable):
					for case in cases: case.contour(ax, 'ESTS_xt_jprb%i.dat'%j, n, levels=levels)
				else:
					case = cases
					case.contour(ax, 'ESTS_xt_jprb%i.dat'%j, n, levels=levels, colors="black", linestyles="--")
					case.contour(ax, 'ESTS_LAMW_xt_jprb%i.dat'%j, n, levels=levels, colors="red", linestyles='-')

				ax.set_xlim(self.k_x_plus_lim)
				ax.set_ylim(self.k_t_plus_lim)

				if ax in axs[:,-1]:
					ax2 = ax.twinx()
					ax2.set_yticks([])
					ax2.set_ylabel(ax.get_title(),
						horizontalalignment='left',
						verticalalignment='center',
						rotation="horizontal")
				if ax not in axs[-1] : ax.set_xlabel('')
				if ax not in axs[:,0]: ax.set_ylabel('')
				ax.set_title( r"$y^+$ = %.0f"%yp if (ax in axs[0]) else '')

		self.save(fig, figname)

	def plot_TimeSpaceCorrelation(self, cases, figname='TimeSpaceCorrelation'):
		ns = (1, 2, 3, 4)
		js = (1, 2, 5)
		yps = (5,15,100)
		levels = (0.2, 0.4, 0.8)

		fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(6, 6))
		
		for axr, n in zip(axs, ns):
			for ax, yp, j in zip(axr, yps, js):

				if isinstance(cases, Iterable):
					for case in cases: case.contour(ax, 'CORTS_xt_jprb%i.dat'%j, n, levels=levels)
				else:
					case = cases
					case.contour(ax, 'CORTS_xt_jprb%i.dat'%j, n, levels=levels, colors="black", linestyles="--")
					case.contour(ax, 'CORTS_ELIP_xt_jprb%i.dat'%j, n, levels=levels, colors="red", linestyles='-')

				ax.set_xlim([-800, 800])
				ax.set_ylim([-60, 60])

				if ax in axs[:,-1]:
					ax2 = ax.twinx()
					ax2.set_yticks([])
					ax2.set_ylabel(ax.get_title(),
						horizontalalignment='left',
						verticalalignment='center',
						rotation="horizontal")
				if ax not in axs[-1] : ax.set_xlabel('')
				if ax not in axs[:,0]: ax.set_ylabel('')
				ax.set_title( r"$y^+$ = %.0f"%yp if (ax in axs[0]) else '')

		self.save(fig, figname)


	def plot_EllipticPara(self, cases, figname='EllipticPara'):
		ns1 = (1,2,3,4)
		ns2 = (5,6,7,8)

		fig, axs = plt.subplots(2, 2, sharex=True, sharey=True, num=figname, figsize=(6, 4))

		for ax, n1, n2 in zip(np.ravel(axs), ns1, ns2):

			if isinstance(cases, Iterable):
				for case in cases: case.curve(ax, "elip_plot.dat", n1)
				ylabel1, legends = ax.get_ylabel(), [case.name for case in cases]

				for case in cases: case.curve(ax, "elip_plot.dat", n2)
				ylabel2 = ax.get_ylabel()

			else:
				case = cases

				case.curve(ax, "ESTS_convswep.dat", n1, color="black", ls='', marker='d')
				case.curve(ax, "elip_plot.dat", n1, color="red", ls='-')
				ylabel1, legends = ax.get_ylabel(), ["space-time data", "space data"]

				case.curve(ax, "ESTS_convswep.dat", n2, color="black", ls='', marker='d')
				case.curve(ax, "elip_plot.dat", n2, color="red", ls='-')
				ylabel2 = ax.get_ylabel()

			ax.set_xlim(self.y_plus_lim)
			ax.set_ylim([0, 20])

			ax.set_ylabel(ylabel1+'\n\n'+ylabel2,
				horizontalalignment='right',
				verticalalignment='center',
				rotation="horizontal")
			if ax not in axs[-1]: ax.set_xlabel('')

		axs[0,0].legend(legends, loc='upper left', fontsize=8, handlelength=5, frameon=False)
		
		self.save(fig, figname)


	def plot_LAMWPara(self, cases, figname='LAMWPara'):
		ns1 = (1,2,3,4)
		ns2 = (5,6,7,8)
		js = (1,3,5)

		fig, axs = plt.subplots(2, 2, sharex=True, sharey=True, num=figname, figsize=(6, 4))

		for ax, n1, n2 in zip(np.ravel(axs), ns1, ns2):
			for j in js:

				if isinstance(cases, Iterable):
					for case in cases: case.curve(ax, "lamw_plot_jprb%i.dat"%j, n1, lw=1)
					ylabel1, legends = ax.get_ylabel(), [case.name for case in cases]

					for case in cases: case.curve(ax, "lamw_plot_jprb%i.dat"%j, n2, lw=1)
					ylabel2 = ax.get_ylabel()

				else:
					case = cases

					case.curve(ax, "ESTS_moments_jprb%i.dat"%j, n1, color="black", ls="--", lw=1)
					case.curve(ax, "lamw_plot_jprb%i.dat"%j, n1, color="red", ls='-', lw=1)
					ylabel1, legends = ax.get_ylabel(), ["space-time data", "space data"]

					case.curve(ax, "ESTS_moments_jprb%i.dat"%j, n2, color="black", ls="--", lw=1)
					case.curve(ax, "lamw_plot_jprb%i.dat"%j, n2, color="red", ls='-', lw=1)
					ylabel2 = ax.get_ylabel()

			ax.set_xlim(self.k_x_plus_lim)
			ax.set_ylim([0, 25])

			ax.set_ylabel(ylabel1+'\n\n'+ylabel2,
				horizontalalignment='right',
				verticalalignment='center',
				rotation="horizontal")
			if ax not in axs[-1]: ax.set_xlabel('')

			ax.annotate(r"$y^+$ increase", xy=(0.1, 18), xytext=(0.05, 5), fontsize=7, arrowprops=dict(arrowstyle="->"))
			ax.annotate(r"$y^+$ increase", xy=(0.1, 0 ), xytext=(0.05, 5), fontsize=7, arrowprops=dict(arrowstyle="->"))

		axs[0,0].legend(legends, loc='upper left', fontsize=8, handlelength=5, frameon=False)

		self.save(fig, figname)

	def plot_Components(self, case):
		js = (1, 5)
		yps = (5, 100)
		ns1 = (1,2,3,4)
		ns2 = (5,6,7,8)
		colors = ("red", "blue", "green", "black")
		styles = ('-', "-.", ':', "--")
		legends = ["uu", "vv", "ww", "pp"]


		figname = "EllipticPara_Comp"

		fig, ax = plt.subplots(num=figname, figsize=(4, 4))

		for ns in [ns1, ns2]:
			for n,c,s in zip(ns, colors, styles):
				case.curve(ax, "elip_plot.dat", n, color=c, ls=s)

		ax.set_xlim(self.y_plus_lim)
		ax.set_ylim([0, 20])

		legends = ["uu", "vv", "ww", "pp"]
		ax.legend(legends, fontsize=8, handlelength=5, frameon=False)
		ax.set_ylabel("\n\n".join([r"$U^+$", r"$V^+$"]),
			horizontalalignment='right',
			verticalalignment='center',
			rotation="horizontal")

		case.plot.mark_out(ax, xs=[yps], color="grey", lw=0.8)

		self.save(fig, figname)


		for j, yp in zip(js, yps):

			figname = "LAMWPara%.0f_Comp"%yp

			fig, ax = plt.subplots(num=figname, figsize=(4, 4))

			for ns in [ns1, ns2]:
				for n,c,s in zip(ns, colors, styles):
					case.curve(ax, "lamw_plot_jprb%i.dat"%j, n, color=c, ls=s)

			ax.set_xlim(self.k_x_plus_lim)
			ax.set_ylim([0, 20])

			legends = ["uu", "vv", "ww", "pp"]
			ax.legend(legends, fontsize=8, handlelength=5, frameon=False)
			ax.set_ylabel("\n\n".join([ r"$\frac{-\omega_c^+}{k_x^+}$", r"$\frac{\sqrt{B^+}}{k_x^+}$" ]),
				horizontalalignment='right',
				verticalalignment='center',
				rotation="horizontal")

			yticks = []
			for n in (1, 4, 5) if j==1 else (1, 5):
				data = case.plot.getData(case.path+"elip_plot.dat", n)
				yticks += list( np.interp([yp], data[:,0], data[:,-1]) )
			case.plot.mark_out(ax, ys=yticks, color="grey", lw=0.8)

			ax.text(0.1, yticks[0 ]-1.1, r"$U_{uu}^+$ = %.1f"%yticks[0 ], fontsize=7)
			ax.text(0.1, yticks[-1]+0.5, r"$V_{uu}^+$ = %.1f"%yticks[-1], fontsize=7)
			if j==1:
				ax.text(0.1, yticks[1]+0.5, r"$U_{pp}^+$ = %.1f"%yticks[1], fontsize=7)

			self.save(fig, figname)



figs = Figures()

M1000 = Case("/back1/cuigx2_back1/whn/data/DNS1000M/postdata/figures/", name="M1000", color="red", style="-")
M2000 = Case("/back1/cuigx2_back1/whn/data/DNS2000M/postdata/figures/", name="M2000", color="blue", style="-.")
M4000 = Case("/back1/cuigx2_back1/whn/data/DNS4000M/postdata/figures/", name="M4000", color="green", style=":")
F1000 = Case("/back1/cuigx2_back1/whn/data/DNS1000F/postdata/figures/", name="F1000", color="black", style="--")




# figs.plot_MeanU([M1000, M2000, M4000, F1000])
# figs.plot_FlucIntens([M1000, M2000, M4000, F1000])
# figs.plot_TimeSpaceSpectra([M1000, F1000], figname="TimeSpaceSpectra_MvsF")
# figs.plot_TimeSpaceCorrelation([M1000, F1000], figname="TimeSpaceCorrelation_MvsF")

# figs.plot_EllipticPara(M1000, figname="EllipticPara_M1000")
# figs.plot_LAMWPara(M1000, figname="LAMWPara_M1000")
# figs.plot_TimeSpaceSpectra(M1000, figname="TimeSpaceSpectra_M1000")
# figs.plot_TimeSpaceCorrelation(M1000, figname="TimeSpaceCorrelation_M1000")


# figs.plot_TimeSpaceSpectra([M1000, M2000, M4000], figname="TimeSpaceSpectra_Re")
# figs.plot_TimeSpaceCorrelation([M1000, M2000, M4000], figname="TimeSpaceCorrelation_Re")
# figs.plot_EllipticPara([M1000, M2000, M4000], figname="EllipticPara_Re")
# figs.plot_LAMWPara([M1000, M2000, M4000], figname="LAMWPara_Re")
figs.plot_Components(M1000)


exit()




case_names = ['M1000', 'M2000', 'M4000', 'F1000']
plot_colors = {'M1000':'blue', 'M2000':'red', 'M4000':'green', 'F1000':'black'}
plot_styles = {'M1000':'-', 'M2000':'--', 'M4000':'-.', 'F1000':':'}
plot_markers = {'M1000':'s', 'M2000':'^', 'M4000':'v', 'F1000':'o'}
file_paths = {}
for case_name in case_names:
	file_paths[case_name] = '/back1/cuigx2_back1/whn/data/DNS%s/postdata/figures/'%(case_name[1:]+case_name[0])
figure_path = 'figures/'
js = [1,2,3,4,5]
ns = [1,2,3,4]

# figure parameters
lambda_x_plus_lim = [20, 6e3]
lambda_z_plus_lim = [10, 3e3]
k_x_plus_lim = [-0.35,0.35] # ??? untested  一阶矩二阶矩图片加上UV
k_t_plus_lim = [-5.1,5.1]
y_plus_lim = [1, 500]

# data parameters
y_plus = np.zeros(0)
j_probes = np.zeros(0, dtype=int)
Re_tau = u_tau = delta_nu = t_nu = tau_w = 0

# basic functions
def set_path(case_name):
	global y_plus, j_probes, Re_tau, u_tau, delta_nu, t_nu, tau_w
	path = file_paths[case_name]
	y_plus = np.loadtxt(open(path+'y_plus.dat'))
	j_probes = np.array([ int(n) for n in np.ravel(np.loadtxt(open(path+'j_probes.dat'))) ])
	Re_tau = np.loadtxt(open(path+'Re_tau.dat'))
	u_tau = np.loadtxt(open(path+'u_tau.dat'))
	delta_nu = 1.0 / Re_tau
	t_nu = delta_nu / u_tau
	tau_w = u_tau**2
	return path





### basic statistics

figname = 'Mean_U'
fig, ax = plt.figure(num=figname, figsize=(3, 3)), plt.gca()
for case_name in case_names:
	path = set_path(case_name)
	labels = plot_line(ax, path+'means_plot.dat', 1, color=plot_colors[case_name], linestyle=plot_styles[case_name])
ax.legend(case_names, fontsize=7.5, loc='upper left', handlelength=5, frameon=False)
ax.set_xlim(y_plus_lim)
ax.set_ylim([0,25])
ax.set_xlabel(labels[0])
ax.set_ylabel(labels[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()

figname = 'FlucIntens'
fig, axs = plt.subplots(2, 2, sharex=True, num=figname, figsize=(6, 4))
ylims = ([0,10], [0,1.5], [0,2.4], [0,10])
for n in range(4):
	ax = axs.ravel()[n]
	for case_name in case_names:
		path = set_path(case_name)
		labels = plot_line(ax, path+'statis_plot.dat', (1,2,3,5)[n], color=plot_colors[case_name], linestyle=plot_styles[case_name])
	if n == 1:
		ax.legend(case_names, fontsize=7.5, loc='upper left', handlelength=5, frameon=False)
	ax.set_xlim(y_plus_lim)
	ax.set_ylim(ylims[n])
	if n in [2, 3]:
		ax.set_xlabel(labels[0])
	ax.set_ylabel(labels[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()



figname = 'EnergySpectra1D'
fig, axs = plt.subplots(len(ns), 2, sharex='col', sharey='row', squeeze=False, num=figname, figsize=(6, 3*len(ns)))
contour_levels = [
	[(0.125, 0.25, 0.5, 1.0), (0.2, 0.4, 0.8, 1.6)],
	[(0.025, 0.05, 0.1 ,0.175), (0.035, 0.07, 0.14, 0.28)],
	[(0.05, 0.1, 0.2, 0.3), (0.045, 0.09, 0.18, 0.36)],
	[(0.2, 0.6, 1.0, 1.4), (0.15,0.3,0.6,1.2)]	]
for col in range(2):
	for row in range(len(ns)):
		ax = axs[row, col]
		for case_name in case_names:
			path = set_path(case_name)
			file_name = ('ES1D_xy.dat', 'ES1D_zy.dat') [col]
			labels,cs = plot_contour(ax, path+file_name, ns[row], levels=contour_levels[row][col], colors=plot_colors[case_name], linestyles=plot_styles[case_name])
		ax.set_xlim( (lambda_x_plus_lim, lambda_z_plus_lim) [col] )
		ax.set_ylim([1,1000])
		ax.set_xscale('log')
		ax.set_yscale('log')
		ax.set_title(labels[2])
		if row == len(ns)-1:
			ax.set_xlabel(labels[0])
		if col == 0:
			ax.set_ylabel(labels[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()


for case_name in case_names:
	path = set_path(case_name)

	figname = 'EnergySpectra2D_%s'%case_name
	fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(3*len(js), 3*len(ns)))
	for col in range(len(js)):
		for row in range(len(ns)):
			ax = axs[row, col]
			file_name = 'ES2D_xz_jprb%i.dat' %js[col]
			labels,cs = plot_contour(ax, path+file_name, ns[row])
			ax.set_xlim(lambda_x_plus_lim)
			ax.set_ylim(lambda_z_plus_lim)
			ax.set_xscale('log')
			ax.set_yscale('log')
			ax.set_title(labels[2]+r", $y^+$ = %.0f" %y_plus[j_probes[js[col]]])
			if row == len(ns)-1:
				ax.set_xlabel(labels[0])
			if col == 0:
				ax.set_ylabel(labels[1])
	fig.tight_layout()
	fig.savefig(figure_path+figname+'.png', dpi=200)
	plt.close()




### space-time DNS results

figname = 'TimeSpaceSpectra'
fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(3*len(js), 3*len(ns)))
for col in range(len(js)):
	for row in range(len(ns)):
		ax = axs[row, col]
		for case_name in case_names:
			try:
				path = set_path(case_name)
				file_name = 'ESTS_xt_jprb%i.dat' %js[col]
				labels,cs = plot_contour(ax, path+file_name, ns[row], levels=(-3, -1, 1), colors=plot_colors[case_name], linestyles=plot_styles[case_name])
				# if case_name == case_names[-1]:
					# ax.clabel(cs)
			except IOError:
				pass
		ax.set_xlim(k_x_plus_lim)
		ax.set_ylim(k_t_plus_lim)
		ax.set_title( labels[2]+r", $y^+$ = %.0f" %y_plus[j_probes[js[col]]] ) # y_plus of the last file
		if row == len(ns)-1:
			ax.set_xlabel(labels[0])
		if col == 0:
			ax.set_ylabel(labels[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()

figname = 'TimeSpaceCorrelation'
fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(3*len(js), 3*len(ns)))
for col in range(len(js)):
	for row in range(len(ns)):
		ax = axs[row, col]
		for case_name in case_names:
			try:
				path = set_path(case_name)
				file_name = 'CORTS_xt_jprb%i.dat' %js[col]
				labels,cs = plot_contour(ax, path+file_name, ns[row], levels=(0.2,0.4,0.8), colors=plot_colors[case_name], linestyles=plot_styles[case_name])
				# if case_name == case_names[-1]:
					# ax.clabel(cs)
			except IOError:
				pass
		ax.set_xlim([-740,740])
		ax.set_ylim([-50,50])
		ax.set_title( labels[2]+r", $y^+$ = %.0f" %y_plus[j_probes[js[col]]] ) # y_plus of the last file
		if row == len(ns)-1:
			ax.set_xlabel(labels[0])
		if col == 0:
			ax.set_ylabel(labels[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()


figname = 'EllipticPara_TS'
fig, axs = plt.subplots(len(ns), 1, sharex=True, sharey=True, squeeze=False, num=figname, figsize=(4, 3*len(ns)))
for row in range(len(ns)):
	ax = axs[row,0]
	legends = []
	for case_name in case_names:
		try:
			path = set_path(case_name)
			labels1 = plot_line(ax, path+'ESTS_convswep.dat', ns[row], color=plot_colors[case_name], linestyle=plot_styles[case_name], marker='^')
			legends.append(case_name)
		except IOError:
			pass
	for case_name in case_names:
		try:
			path = set_path(case_name)
			labels2 = plot_line(ax, path+'ESTS_convswep.dat', ns[row]+4, color=plot_colors[case_name], linestyle=plot_styles[case_name], marker='v')
		except IOError:
			pass
	if row == 0:
		ax.legend(np.array([[cn+' U', cn+' V'] for cn in legends]).T.ravel(), fontsize=7.5, loc='upper left', ncol=2, handlelength=5, numpoints=2, frameon=False)
	ax.set_xlim(y_plus_lim) # point y=0 will be excluded as long as log scale is used
	ax.set_ylim([0, 25])
	if row == len(ns)-1:
		ax.set_xlabel(labels1[0])
	ax.set_ylabel(labels1[1]+', '+labels2[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()


figname = 'EllipticPara_components_cmp_TS'
fig, axs = plt.subplots(len(case_names), 1, sharex=True, sharey=True, squeeze=False, num=figname, figsize=(4, 4*len(case_names)))
for row in range(len(case_names)):
	ax = axs[row,0]
	case_name = case_names[row]
	try:
		path = set_path(case_name)
		for n in range(1,5):
			labels = plot_line(ax, path+'ESTS_convswep.dat', n, color=plot_colors.values()[n-1], linestyle=plot_styles.values()[n-1], marker='^')
		for n in range(5,9):
			labels = plot_line(ax, path+'ESTS_convswep.dat', n, color=plot_colors.values()[n-5], linestyle=plot_styles.values()[n-5], marker='v')
	except IOError:
		pass
	if row == 0:
		ax.legend(fontsize=7.5, loc='upper left', ncol=2, handlelength=5, numpoints=2, frameon=False)
	ax.set_xlim(y_plus_lim)
	ax.set_ylim([0, 25])
	ax.set_title(case_name)
	if row == len(case_names)-1:
		ax.set_xlabel(labels[0])
	ax.set_ylabel(r"$U^+, V^+$")
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()



figname = 'LAMWPara_TS'
fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(3*len(js), 3*len(ns)))
for col in range(len(js)):
	for row in range(len(ns)):
		ax = axs[row, col]
		legends = []
		for case_name in case_names:
			try:
				path = set_path(case_name)
				file_name = 'ESTS_moments_jprb%i.dat' %js[col]
				labels1 = plot_line(ax, path+file_name, ns[row], color=plot_colors[case_name], linestyle=plot_styles[case_name], marker='^', markevery=40)
				legends.append(case_name)
			except IOError:
				pass
		for case_name in case_names:
			try:
				path = set_path(case_name)
				file_name = 'ESTS_moments_jprb%i.dat' %js[col]
				labels2 = plot_line(ax, path+file_name, ns[row]+4, color=plot_colors[case_name], linestyle=plot_styles[case_name], marker='v', markevery=40)
			except IOError:
				pass
		if row == 0 and col == 0:
			ax.legend(np.array([[cn+r" $\omega_c$", cn+r" B"] for cn in legends]).T.ravel(), fontsize=7.5, loc='upper left', ncol=2, handlelength=5, numpoints=2, frameon=False)
		ax.set_xscale('linear')
		ax.set_xlim([0, max(k_x_plus_lim)])
		ax.set_ylim([0, max(k_t_plus_lim)])
		if row == 0:
			ax.set_title( r"$y^+$ = %.0f" %y_plus[j_probes[js[col]]] ) # y_plus of the last file
		if row == len(ns)-1:
			ax.set_xlabel(labels1[0])
		if col == 0:
			ax.set_ylabel(labels1[1]+', '+labels2[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()


figname = 'LAMWPara_components_cmp_TS'
fig, axs = plt.subplots(len(case_names), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(4*len(js), 4*len(case_names)))
for col in range(len(js)):
	for row in range(len(case_names)):
		ax = axs[row, col]

		case_name = case_names[row]
		try:
			path = set_path(case_name)
			file_name = 'ESTS_moments_jprb%i.dat' %js[col]
			for n in range(1,5):
				labels = plot_line(ax, path+file_name, n, color=plot_colors.values()[n-1], linestyle=plot_styles.values()[n-1], marker='^', markevery=40)
			for n in range(5,9):
				labels = plot_line(ax, path+file_name, n, color=plot_colors.values()[n-5], linestyle=plot_styles.values()[n-5], marker='v', markevery=40)
		except IOError:
			pass

		if row == 0 and col == 0:
			ax.legend(fontsize=7.5, loc='upper left', ncol=2, handlelength=5, numpoints=2, frameon=False)
		ax.set_xscale('linear')
		ax.set_xlim([0, max(k_x_plus_lim)])
		ax.set_ylim([0, max(k_t_plus_lim)])
		ax.set_title( case_name + r", $y^+$ = %.0f" %y_plus[j_probes[js[col]]] ) # y_plus of the last file
		if row == len(case_names)-1:
			ax.set_xlabel(labels[0])
		if col == 0:
			ax.set_ylabel(r"$-\omega_c^+, \sqrt{B^+}$")
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()







## time derivative result

figname = 'ConvecVelo1D_x'
fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(3*len(js), 3*len(ns)))
for col in range(len(js)):
	for row in range(len(ns)):
		ax = axs[row, col]
		legends = []
		for case_name in case_names:
			try:
				path = set_path(case_name)
				file_name = 'CONV1D_x_jprb%i.dat' %js[col]
				labels = plot_line(ax, path+file_name, ns[row], color=plot_colors[case_name], linestyle=plot_styles[case_name])
				legends.append(case_name)
			except IOError:
				pass
		if row == 0 and col == 0:
			ax.legend(legends, fontsize=7.5, loc='upper left', handlelength=5, frameon=False)
		ax.set_xlim(lambda_x_plus_lim)
		ax.set_ylim([7, 18])
		if row == 0:
			ax.set_title( r"$y^+$ = %.0f" %y_plus[j_probes[js[col]]] ) # y_plus of the last file
		if row == len(ns)-1:
			ax.set_xlabel(labels[0])
		if col == 0:
			ax.set_ylabel(labels[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()


figname = 'ConvecVelo1D_z'
fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(3*len(js), 3*len(ns)))
for col in range(len(js)):
	for row in range(len(ns)):
		ax = axs[row, col]
		legends = []
		for case_name in case_names:
			try:
				path = set_path(case_name)
				file_name = 'CONV1D_z_jprb%i.dat' %js[col]
				labels = plot_line(ax, path+file_name, ns[row], color=plot_colors[case_name], linestyle=plot_styles[case_name])
				legends.append(case_name)
			except IOError:
				pass
		if row == 0 and col == 0:
			ax.legend(legends, fontsize=7.5, loc='upper left', handlelength=5, frameon=False)
		ax.set_xlim(lambda_z_plus_lim)
		ax.set_ylim([7, 18])
		if row == 0:
			ax.set_title( r"$y^+$ = %.0f" %y_plus[j_probes[js[col]]] ) # y_plus of the last file
		if row == len(ns)-1:
			ax.set_xlabel(labels[0])
		if col == 0:
			ax.set_ylabel(labels[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()


for case_name in case_names:
	try:
		path = set_path(case_name)

		figname = 'ConvecVelo2D_%s'%case_name
		fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(3*len(js), 3*len(ns)))
		for col in range(len(js)):
			for row in range(len(ns)):
				ax = axs[row, col]
				file_name = 'CONV2D_xz_jprb%i.dat' %js[col]
				labels,cs = plot_contour(ax, path+file_name, ns[row], filled=1, levels=range(7,19))
				file_name = 'ES2D_xz_jprb%i.dat' %js[col]
				plot_contour(ax, path+file_name, ns[row], colors='black')
				# ax.clabel(cs, fmt='%i')
				ax.set_xlim(lambda_x_plus_lim)
				ax.set_ylim(lambda_z_plus_lim)
				ax.set_xscale('log')
				ax.set_yscale('log')
				ax.set_title(labels[2]+r", $y^+$ = %.0f" %y_plus[j_probes[js[col]]])
				if row == len(ns)-1:
					ax.set_xlabel(labels[0])
				if col == 0:
					ax.set_ylabel(labels[1])
		fig.tight_layout()
		fig.subplots_adjust(right=0.95)
		fig.colorbar(cs, cax=plt.axes([0.96,0.06,0.01,0.9]), format='%i', ticks=cs.levels, extendrect=True)
		fig.savefig(figure_path+figname+'.png', dpi=200)
	
		plt.close()
	except IOError:
		pass








figname = 'EllipticPara_S'
fig, axs = plt.subplots(len(ns), 1, sharex=True, sharey=True, squeeze=False, num=figname, figsize=(4, 3*len(ns)))
for row in range(len(ns)):
	ax = axs[row,0]
	legends = []
	for case_name in case_names:
		try:
			path = set_path(case_name)
			labels1 = plot_line(ax, path+'elip_plot.dat', ns[row], color=plot_colors[case_name], linestyle=plot_styles[case_name], marker='^', markevery=25)
			legends.append(case_name)
		except IOError:
			pass
	for case_name in case_names:
		try:
			path = set_path(case_name)
			labels2 = plot_line(ax, path+'elip_plot.dat', ns[row]+4, color=plot_colors[case_name], linestyle=plot_styles[case_name], marker='v', markevery=25)
		except IOError:
			pass
	if row == 0:
		ax.legend(np.array([[cn+' U', cn+' V'] for cn in legends]).T.ravel(), fontsize=7.5, loc='upper left', ncol=2, handlelength=5, numpoints=2, frameon=False)
	ax.set_xlim(y_plus_lim)
	ax.set_ylim([0, 25])
	if row == len(ns)-1:
		ax.set_xlabel(labels1[0])
	ax.set_ylabel(labels1[1]+', '+labels2[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()

figname = 'EllipticPara_components_cmp_S'
fig, axs = plt.subplots(len(case_names), 1, sharex=True, sharey=True, squeeze=False, num=figname, figsize=(4, 4*len(case_names)))
for row in range(len(case_names)):
	ax = axs[row,0]
	case_name = case_names[row]
	try:
		path = set_path(case_name)
		for n in range(1,5):
			labels = plot_line(ax, path+'elip_plot.dat', n, color=plot_colors.values()[n-1], linestyle=plot_styles.values()[n-1], marker='^', markevery=25)
		for n in range(5,9):
			labels = plot_line(ax, path+'elip_plot.dat', n, color=plot_colors.values()[n-5], linestyle=plot_styles.values()[n-5], marker='v', markevery=25)
	except IOError:
		pass
	if row == 0:
		ax.legend(fontsize=7.5, loc='upper left', ncol=2, handlelength=5, numpoints=2, frameon=False)
	ax.set_xlim(y_plus_lim)
	ax.set_ylim([0, 25])
	ax.set_title(case_name)
	if row == len(case_names)-1:
		ax.set_xlabel(labels[0])
	ax.set_ylabel(r"$U^+, V^+$")
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()

for case_name in case_names:
	try:
		path = set_path(case_name)


		figname = 'EllipticPara_cmp_%s'%case_name
		fig, axs = plt.subplots(len(ns), 1, sharex=True, sharey=True, squeeze=False, num=figname, figsize=(4, 3*len(ns)))

		for row in range(len(ns)):
			ax = axs[row,0]
			legends = []
			labels1 = plot_line(ax, path+'ESTS_convswep.dat', ns[row], color='black', linestyle='--', marker='^')
			legends.append(labels1[1]+' space-time data')
			labels1 = plot_line(ax, path+'elip_plot.dat', ns[row], color='red', linestyle='-', marker='^', markevery=25)
			legends.append(labels1[1]+' space data')
			labels2 = plot_line(ax, path+'ESTS_convswep.dat', ns[row]+4, color='black', linestyle='--', marker='v')
			legends.append(labels2[1]+' space-time data')
			labels2 = plot_line(ax, path+'elip_plot.dat', ns[row]+4, color='red', linestyle='-', marker='v', markevery=25)
			legends.append(labels2[1]+' space data')

			ax.legend(legends, fontsize=7.5, loc='upper left', handlelength=5, numpoints=2, frameon=False)
			ax.set_xlim(y_plus_lim)
			ax.set_ylim([0, 25])
			if row == len(ns)-1:
				ax.set_xlabel(labels1[0])
			ax.set_ylabel(labels1[1]+', '+labels2[1])
		fig.tight_layout()
		fig.savefig(figure_path+figname+'.png', dpi=200)
	
		plt.close()


		figname = 'TimeSpaceCorrelation_elip_cmp_%s'%case_name
		fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(3*len(js), 3*len(ns)))
		for col in range(len(js)):
			for row in range(len(ns)):
				ax = axs[row,col]

				file_name = 'CORTS_xt_jprb%i.dat' %js[col]
				labels,cs = plot_contour(ax, path+file_name, ns[row], levels=(0.2,0.4,0.8), colors='black', linestyles='--')

				file_name = 'CORTS_ELIP_xt_jprb%i.dat' %js[col]
				labels,cs = plot_contour(ax, path+file_name, ns[row], levels=(0.2,0.4,0.8), colors='red', linestyles='-')

				# ax.clabel(cs)
				ax.set_xlim([-740,740])
				ax.set_ylim([-50,50])
				ax.set_title( labels[2]+r", $y^+$ = %.0f" %y_plus[j_probes[js[col]]] ) # y_plus of the last file
				if row == len(ns)-1:
					ax.set_xlabel(labels[0])
				if col == 0:
					ax.set_ylabel(labels[1])
		fig.tight_layout()
		fig.savefig(figure_path+figname+'.png', dpi=200)
	
		plt.close()

	except IOError:
		pass








figname = 'LAMWPara_S'
fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(3*len(js), 3*len(ns)))
for col in range(len(js)):
	for row in range(len(ns)):
		ax = axs[row, col]
		legends = []
		for case_name in case_names:
			try:
				path = set_path(case_name)
				file_name = 'lamw_plot_jprb%i.dat' %js[col]
				labels1 = plot_line(ax, path+file_name, ns[row], color=plot_colors[case_name], linestyle=plot_styles[case_name], marker='^', markevery=40)
				legends.append(case_name)
			except IOError:
				pass
		for case_name in case_names:
			try:
				path = set_path(case_name)
				file_name = 'lamw_plot_jprb%i.dat' %js[col]
				labels2 = plot_line(ax, path+file_name, ns[row]+4, color=plot_colors[case_name], linestyle=plot_styles[case_name], marker='v', markevery=40)
			except IOError:
				pass
		if row == 0 and col == 0:
			ax.legend(np.array([[cn+r" $\omega_c$", cn+r" B"] for cn in legends]).T.ravel(), fontsize=7.5, loc='upper left', ncol=2, handlelength=5, numpoints=2, frameon=False)
		ax.set_xscale('linear')
		ax.set_xlim([0, max(k_x_plus_lim)])
		ax.set_ylim([0, max(k_t_plus_lim)])
		if row == 0:
			ax.set_title( r"$y^+$ = %.0f" %y_plus[j_probes[js[col]]] ) # y_plus of the last file
		if row == len(ns)-1:
			ax.set_xlabel(labels1[0])
		if col == 0:
			ax.set_ylabel(labels1[1]+', '+labels2[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()


figname = 'LAMWPara_components_cmp_S'
fig, axs = plt.subplots(len(case_names), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(4*len(js), 4*len(case_names)))
for col in range(len(js)):
	for row in range(len(case_names)):
		ax = axs[row, col]

		case_name = case_names[row]
		try:
			path = set_path(case_name)
			file_name = 'lamw_plot_jprb%i.dat' %js[col]
			for n in range(1,5):
				labels = plot_line(ax, path+file_name, n, color=plot_colors.values()[n-1], linestyle=plot_styles.values()[n-1], marker='^', markevery=40)
			for n in range(5,9):
				labels = plot_line(ax, path+file_name, n, color=plot_colors.values()[n-5], linestyle=plot_styles.values()[n-5], marker='v', markevery=40)
		except IOError:
			pass

		if row == 0 and col == 0:
			ax.legend(fontsize=7.5, loc='upper left', ncol=2, handlelength=5, numpoints=2, frameon=False)
		ax.set_xscale('linear')
		ax.set_xlim([0, max(k_x_plus_lim)])
		ax.set_ylim([0, max(k_t_plus_lim)])
		ax.set_title( case_name + r", $y^+$ = %.0f" %y_plus[j_probes[js[col]]] ) # y_plus of the last file
		if row == len(case_names)-1:
			ax.set_xlabel(labels[0])
		if col == 0:
			ax.set_ylabel(r"$-\omega_c^+, \sqrt{B^+}$")
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()


for case_name in case_names:
	try:
		path = set_path(case_name)


		figname = 'LAMWPara_cmp_%s'%case_name
		fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(3*len(js), 3*len(ns)))
		for col in range(len(js)):
			for row in range(len(ns)):
				ax = axs[row, col]
				legends = []

				file_name = 'ESTS_moments_jprb%i.dat' %js[col]
				labels1 = plot_line(ax, path+file_name, ns[row], color='black', linestyle='--', marker='^', markevery=40)
				legends.append(labels1[1]+' space-time data')
				file_name = 'lamw_plot_jprb%i.dat' %js[col]
				labels1 = plot_line(ax, path+file_name, ns[row], color='red', linestyle='-', marker='^', markevery=40)
				legends.append(labels1[1]+' space data')

				file_name = 'ESTS_moments_jprb%i.dat' %js[col]
				labels2 = plot_line(ax, path+file_name, ns[row]+4, color='black', linestyle='--', marker='v', markevery=40)
				legends.append(labels2[1]+' space-time data')
				file_name = 'lamw_plot_jprb%i.dat' %js[col]
				labels2 = plot_line(ax, path+file_name, ns[row]+4, color='red', linestyle='-', marker='v', markevery=40)
				legends.append(labels2[1]+' space data')

				if col == 0:
					ax.legend(legends, fontsize=7.5, loc='upper left', handlelength=5, numpoints=2, frameon=False)
				ax.set_xscale('linear')
				ax.set_xlim([0, max(k_x_plus_lim)])
				ax.set_ylim([0, max(k_t_plus_lim)])
				if row == 0:
					ax.set_title( r"$y^+$ = %.0f" %y_plus[j_probes[js[col]]] ) # y_plus of the last file
				if row == len(ns)-1:
					ax.set_xlabel(labels1[0])
				if col == 0:
					ax.set_ylabel(labels1[1]+', '+labels2[1])
		fig.tight_layout()
		fig.savefig(figure_path+figname+'.png', dpi=200)
	
		plt.close()


		figname = 'TimeSpaceSpectra_lamw_cmp_%s'%case_name
		fig, axs = plt.subplots(len(ns), len(js), sharex=True, sharey=True, squeeze=False, num=figname, figsize=(3*len(js), 3*len(ns)))
		for col in range(len(js)):
			for row in range(len(ns)):
				ax = axs[row, col]

				file_name = 'ESTS_xt_jprb%i.dat' %js[col]
				labels,cs = plot_contour(ax, path+file_name, ns[row], levels=(-3, -1, 1), colors='black', linestyles='--')

				file_name = 'ESTS_LAMW_xt_jprb%i.dat' %js[col]
				labels,cs = plot_contour(ax, path+file_name, ns[row], levels=(-3, -1, 1), colors='red', linestyles='-')
				
				# ax.clabel(cs)
				ax.set_xlim(k_x_plus_lim)
				ax.set_ylim(k_t_plus_lim)
				ax.set_title( labels[2]+r", $y^+$ = %.0f" %y_plus[j_probes[js[col]]] )
				if row == len(ns)-1:
					ax.set_xlabel(labels[0])
				if col == 0:
					ax.set_ylabel(labels[1])
		fig.tight_layout()
		fig.savefig(figure_path+figname+'.png', dpi=200)
	
		plt.close()

	except IOError:
		pass







figname = 'MeanProfile'
fig, axs = plt.subplots(2, 2, sharex=True, num=figname, figsize=(6, 4))
ylims = ([0,25], [-1,1], [-1,1], [-1.5,0])
for n in range(4):
	ax = axs.ravel()[n]
	for case_name in case_names:
		path = set_path(case_name)
		labels = plot_line(ax, path+'means_plot.dat', n+1, color=plot_colors[case_name], linestyle=plot_styles[case_name])
	if n == 0:
		ax.legend(case_names, fontsize=7.5, loc='best', handlelength=5, frameon=False)
	ax.set_xlim(y_plus_lim)
	ax.set_ylim(ylims[n])
	if n in [2, 3]:
		ax.set_xlabel(labels[0])
	ax.set_ylabel(labels[1])
# # fig.align_labels()
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()

figname = 'ReynoldsStress'
fig, axs = plt.subplots(2, 2, sharex=True, num=figname, figsize=(6, 4))
ylims = ([0,10], [0,1.5], [0,2.4], [-1,0])
for n in range(4):
	ax = axs.ravel()[n]
	for case_name in case_names:
		path = set_path(case_name)
		labels = plot_line(ax, path+'statis_plot.dat', n+1, color=plot_colors[case_name], linestyle=plot_styles[case_name])
	if n == 0:
		ax.legend(case_names, fontsize=7.5, loc='best', handlelength=5, frameon=False)
	ax.set_xlim(y_plus_lim)
	ax.set_ylim(ylims[n])
	if n in [2, 3]:
		ax.set_xlabel(labels[0])
	ax.set_ylabel(labels[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()

figname = 'PressureCovariance'
fig, axs = plt.subplots(2, 2, sharex=True, num=figname, figsize=(6, 4))
ylims = ([0,10], [-0.2,1], [-0.2,0.05], [-0.5,0.5])
for n in range(4):
	ax = axs.ravel()[n]
	for case_name in case_names:
		path = set_path(case_name)
		labels = plot_line(ax, path+'statis_plot.dat', n+5, color=plot_colors[case_name], linestyle=plot_styles[case_name])
	if n == 0:
		ax.legend(case_names, fontsize=7.5, loc='best', handlelength=5, frameon=False)
	ax.set_xlim(y_plus_lim)
	ax.set_ylim(ylims[n])
	if n in [2, 3]:
		ax.set_xlabel(labels[0])
	ax.set_ylabel(labels[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()

figname = 'VorticityCovariance'
fig, axs = plt.subplots(2, 2, sharex=True, num=figname, figsize=(6, 4))
ylims = ([0,0.06], [0,0.05], [0,0.2], [-0.01,0.02])
for n in range(4):
	ax = axs.ravel()[n]
	for case_name in case_names:
		path = set_path(case_name)
		labels = plot_line(ax, path+'statis_plot.dat', n+9, color=plot_colors[case_name], linestyle=plot_styles[case_name])
	if n == 0:
		ax.legend(case_names, fontsize=7.5, loc='best', handlelength=5, frameon=False)
	ax.set_xlim(y_plus_lim)
	ax.set_ylim(ylims[n])
	if n in [2, 3]:
		ax.set_xlabel(labels[0])
	ax.set_ylabel(labels[1])
fig.tight_layout()
fig.savefig(figure_path+figname+'.png', dpi=200)
plt.close()



