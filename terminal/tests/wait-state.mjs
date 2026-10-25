/** Await actual asynchronous predicates; a Promise's truthiness is never success. */
export async function waitState(page,base,predicate,timeoutMs=10000){
 const deadline=performance.now()+timeoutMs;
 while(performance.now()<deadline){
  const response=await page.request.get(base+'/api/v1/state',{timeout:Math.max(1,Math.min(1000,deadline-performance.now()))});
  if(response.status()!==200)throw new Error('State polling failed: '+response.status());
  if(await predicate(await response.json())===true)return;
  await new Promise(resolve=>setTimeout(resolve,10));
 }
 throw new Error('State predicate did not become true within bounded polling interval');
}
