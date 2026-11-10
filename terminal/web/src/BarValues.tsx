import {barSourceLabel} from './barChart.ts';
import type {Bar,BarSource} from './barChart';
/** Text alternative uses exact accepted strings,never binary64 chart coordinates. */
export function BarValues({bars,source}:{bars:Bar[];source:BarSource}){
 const label=barSourceLabel(source);
 return <div className="atlas-table-scroll" tabIndex={0} role="region" aria-label="Exact historical bar values"><table><caption>{label.title} · exact accepted values · historical,not live</caption><thead><tr><th scope="col">Source timestamp UTC</th><th scope="col">Open</th><th scope="col">High</th><th scope="col">Low</th><th scope="col">Close</th><th scope="col">Provider volume</th></tr></thead><tbody>{bars.map(b=><tr key={b.timestamp}><th scope="row"><time dateTime={b.timestamp}>{b.timestamp}</time></th>{[b.open,b.high,b.low,b.close,b.volume].map((v,i)=><td key={i}>{v}</td>)}</tr>)}</tbody></table><p className="panel-note">Prices retain source price units. Volume retains provider units;no share/lot conversion. Keyboard and assistive-technology users can inspect every accepted value without hovering over the graphic.</p></div>;
}
