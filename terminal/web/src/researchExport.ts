import {MODELS,buildResearchPlot,syntheticResearch} from './research3d.ts';
import type {ResearchModel,ResearchSource} from './research3d.ts';
/** Only the authored public fixture can be exported here. Provider retention rights are independent. */
export function authoredResearchBundle(source:ResearchSource,model:ResearchModel,symbol:string,end:number,depth:number,side:'both'|'bid'|'ask'){
 if(source.id!=='authored-research-v1'||source.origin!=='HISTORICAL_SYNTHETIC'||JSON.stringify(source)!==JSON.stringify(syntheticResearch()))throw Error('Research export requires the unchanged authored fixture;provider observations are not exported');
 if(!MODELS.some(([id])=>id===model)||!source.symbols.includes(symbol)||!Number.isSafeInteger(end)||end<0||end>100000||![3,6,12].includes(depth)||!['both','bid','ask'].includes(side))throw Error('Invalid declared research export parameters');
 const plot=buildResearchPlot(source,model,symbol,end,depth,side);
 return {schema:'gig.authored.research.export.v1',classification:'HISTORICAL_SYNTHETIC',source,parameters:{model,symbol,capture_endpoint:end,depth,side},result:{axes:plot.axes,summary:plot.summary,notes:plot.notes,marks:plot.marks},limitations:['Display geometry is binary64;exact source values remain in source records and inspection labels.','No observed input,provider qualification,predictive accuracy or profitability claim.']};
}
