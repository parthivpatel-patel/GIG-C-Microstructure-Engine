/** Fail before navigation/mutation when an operator has enabled market collection. */
export async function assertFixtureServer(page,base){
 const response=await page.request.get(base+'/api/v1/health',{timeout:5000});
 if(response.status()!==200)throw new Error('Fixture server health unavailable');
 const health=await response.json();
 if(health.fixture_tests_safe!==true)throw new Error('Refusing fixture browser tests:live-enabled/active or observed-data server;start a separate gated test instance');
}
