export type ModelPoint={shock:number;priorVariance:number;variance:number};
export function garchGrid(omega:number,alpha:number,beta:number):ModelPoint[][]{
 if(![omega,alpha,beta].every(Number.isFinite)||omega<0||omega>.01||alpha<0||beta<0||alpha+beta>=1)throw Error('Require nonnegative parameters,omega≤.01 and alpha+beta<1');
 return Array.from({length:21},(_,i)=>Array.from({length:21},(_,j)=>{const shock=(i-10)/100,priorVariance=j*.002;return {shock,priorVariance,variance:omega+alpha*shock*shock+beta*priorVariance}}));
}
