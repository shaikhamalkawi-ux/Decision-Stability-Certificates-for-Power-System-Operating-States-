"""Plot already verified energy evidence; no optimization or new scientific test."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/research_next/fixed_union_figure'
INPUTS = {
    'identity': ('results/research8h/hour_of_day/january_identity/constructive_check.json',
        '4bc4a850eb640021e2566224e0566012be0d7f9ea82b205054b63a11544ae800'),
    'repair': ('results/research_next/day321_local_repair/run01/result.json',
        'ec7bb3be2d79c5c3b878a7d674da5ca6c625173d07cffa440261018d9f452091'),
    'review': ('results/research_next/union_energy_floor/INDEPENDENT_REVIEW.json',
        '4ce224e7242bbad68ccfd5a9a5220b63e0b66d1db97848dda3098fa56743da9e'),
}

def digest(b): return hashlib.sha256(b).hexdigest()
def q(x): return Fraction(int(x['numerator']), int(x['denominator']))

def main():
    assert not OUT.exists(), 'Keep each delivered plot immutable'
    records={}; bindings=[]
    for role,(path,expected) in INPUTS.items():
        b=(ROOT/path).read_bytes(); assert digest(b)==expected
        records[role]=json.loads(b)
        bindings.append(dict(path=path,bytes=len(b),sha256=expected))
    floor_path=ROOT/'results/research_next/union_energy_floor/result.json'
    floor_bytes=floor_path.read_bytes(); floor=json.loads(floor_bytes)
    bindings.append(dict(path=str(floor_path.relative_to(ROOT)),bytes=len(floor_bytes),sha256=digest(floor_bytes)))
    # Exact published values are asserted against the source records, not inferred from pixels.
    identity=q(records['identity']['exact_fossil_MWh'])
    repaired=q(records['repair']['energy_after'])
    assert records['repair']['accepted'] and repaired==identity+60
    assert str(repaired.numerator)=='1659121868587103333305'
    assert str(repaired.denominator)=='72057594037927936'
    necessary=q(floor['worlds'][0]['necessary_fossil_energy_floor'])
    assert necessary==q(floor['worlds'][1]['necessary_fossil_energy_floor'])
    cap=q(floor['worlds'][0]['expanded_cap'])
    assert cap==q(records['repair']['actual_expanded_cap'])
    assert identity<cap and repaired<cap<necessary
    OUT.mkdir(parents=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none'})
    fig,ax=plt.subplots(figsize=(11.5,5.5))
    fig.subplots_adjust(left=.36,right=.96,top=.77,bottom=.28)
    colors=['#176c67','#176c67','#a13b32']; vals=[float(identity),float(repaired),float(necessary)]
    ys=[2,1,0]
    ax.axvline(float(cap),color='#535a65',linestyle=(0,(4,3)),linewidth=1.4,zorder=1)
    ax.text(float(cap)+12,2.64,'Expanded cap: 23,195.00001',color='#535a65',fontsize=10)
    for x,y,c in zip(vals,ys,colors):
        ax.plot(x,y,marker='o',markersize=9,color=c,zorder=3)
        ax.text(x,y+.19,f'{x:,.2f} MWh',ha='center',color=c,fontsize=11,fontweight='bold')
    ax.annotate('',xy=(23870,0),xytext=(vals[2]+12,0),
        arrowprops=dict(arrowstyle='->',color=colors[2],lw=1.7))
    ax.text(23760,-.25,'at least this much',ha='center',color=colors[2],fontsize=9)
    ax.set_yticks(ys,labels=['Identity world\nverified feasible point',
        'Reordered world\nverified repaired point','One common union schedule\nproven necessary lower bound'])
    ax.tick_params(axis='y',length=0,pad=13)
    ax.set_xlim(22750,23900);ax.set_ylim(-.55,2.7)
    ax.set_xticks([22800,23000,23200,23400,23600,23800])
    ax.set_xlabel('Weekly fossil-unit electrical generation (MWh)',labelpad=13)
    ax.grid(axis='x',alpha=.18,zorder=0)
    for side in ['top','right','left']:ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#cccccc')
    fig.text(.05,.94,'Two feasible worlds; one proposed common schedule rejected',
        fontsize=16,fontweight='bold',color='#202c3a')
    fig.text(.05,.875,'The union requires at least 411.6037032 MWh more than the permitted cap.',
        fontsize=11,color='#414c59')
    fig.text(.05,.125,'The points are feasible-witness energies, not optimal costs. The arrow is a lower bound, not a dispatch.',
        fontsize=9.5,color='#414c59')
    fig.text(.05,.075,'Original tolerance-expanded encoding (tau = binary64 1e-5). Other common commitments remain unresolved.',
        fontsize=9.5,color='#414c59')
    for ext in ('png','svg'):
        fig.savefig(OUT/('fixed_union_energy.'+ext),dpi=180,facecolor='white')
    plt.close(fig)
    caption=('Figure: Two individually accepted feasible witnesses and a necessary energy lower bound for their '
        'prescribed common union. The bound rejects that candidate in both original expanded models; it does '
        'not reject all common commitments. Point energies are not optimized objectives. The displayed cap '
        'uses the same exact binary64-derived outward tolerance as the checks. The construction is a standard '
        'linear implication; no new optimization or field experiment is claimed.\n')
    (OUT/'CAPTION.md').write_text(caption,encoding='utf-8')
    for x in bindings: assert digest((ROOT/x['path']).read_bytes())==x['sha256']
    report=dict(inputs=bindings,source_sha256=digest(Path(__file__).read_bytes()),
        data_operation='Visualize already verified results; no scientific replay',
        identity_MWh=str(identity),repaired_MWh=str(repaired),union_lower_bound_MWh=str(necessary),
        expanded_cap_MWh=str(cap),outputs=[])
    for p in sorted(OUT.iterdir()):
        b=p.read_bytes();report['outputs'].append(dict(name=p.name,bytes=len(b),sha256=digest(b)))
    (OUT/'FIGURE_MANIFEST.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(outputs=[x['name'] for x in report['outputs']])))

if __name__=='__main__':main()
