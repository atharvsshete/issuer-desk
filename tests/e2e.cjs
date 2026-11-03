// Optional test dependency: Playwright, plus installed Chrome and Edge.
const assert = require("node:assert/strict");
const path = require("node:path");
const {pathToFileURL} = require("node:url");
const {chromium} = require("playwright");

async function run(channel, width) {
  const browser = await chromium.launch({channel});
  try {
    const page = await browser.newPage({viewport:{width,height:860},offline:true});
    const errors = [];
    page.on("pageerror", e => errors.push(e.message));
    page.on("console", m => { if(m.type()==="error") errors.push(m.text()); });
    page.on("requestfailed", r => errors.push(r.url()));
    page.on("request", r => { if(/^https?:/.test(r.url())) errors.push(r.url()); });
    await page.goto(pathToFileURL(path.join(__dirname,"..","review.html")).href);
    const sel = id => page.locator("#"+id);
    const names = {1:"Alder Funding LLC",2:"Alder Holdings Inc",4:"Alder Holdings Inc",5:"Alder Funding LLC"};
    for (const route of [0,1]) {
      await sel("route").selectOption({index:route});
      for(let n=1;n<=13;n++) {
        await sel("case").selectOption(String(n).padStart(2,"0"));
        const candidate=(route===1 || n<=2) && names[n];
        assert.equal(await sel("candidate").innerText(),candidate || "Hold for research");
        assert.equal(await sel("confirm").isEnabled(),Boolean(candidate));
        assert.equal(await page.locator("#lines mark").count(),candidate ? 1 : 0);
      }
    }
    await sel("case").selectOption("05");
    await sel("confirm").click();
    await page.reload();
    await sel("case").selectOption("05"); // reload returns to exact-label route
    assert.match(await sel("candidate").innerText(),/Confirmed.*Alder Funding LLC/);
    assert.equal(await page.locator("#lines mark").count(),1,"confirmed evidence lost on method change");
    await page.getByText("Decision history",{exact:true}).click();
    assert.match(await sel("audit").innerText(),/Confirmed.*E01.*lines 1.*Local model/);
    await sel("undo").click();
    assert.equal(await sel("candidate").innerText(),"Hold for research");
    assert.match(await sel("audit").innerText(),/Reopened/);
    await sel("case").selectOption("01");
    await sel("confirm").click();
    assert.match(await sel("candidate").innerText(),/Confirmed/);
    await page.getByRole("link",{name:/Compare a filing/}).click();
    assert.equal(new URL(page.url()).hash,"#compare");
    for(const [v,status] of [["A","Only the guarantor changed"],["B","Issuer changed"],["C","Hold for research"]]) {
      await sel("revision").selectOption(v);
      assert.equal(await sel("outcome").innerText(),status);
      assert.equal(await sel("approveRevision").isEnabled(),v==="B");
      assert.match(await sel("before").innerText(),/Issuer: Alder Funding LLC/);
    }
    await sel("revision").selectOption("B");
    await sel("approveRevision").click();
    await page.reload();
    assert.match(await sel("candidate").innerText(),/Confirmed/);
    assert.equal(await sel("outcome").innerText(),"Only the guarantor changed");
    await sel("revision").selectOption("B");
    assert.match(await sel("outcome").innerText(),/Confirmed for B.*Vale Trust Co/);
    await sel("reopenRevision").click();
    await page.getByText("Amendment decision history",{exact:true}).click();
    assert.match(await sel("revisionAudit").innerText(),/Reopened.*Vale Trust Co.*E03/);
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    assert.deepEqual(errors,[]);
    console.log(channel,width,"passed");
  } finally { await browser.close(); }
}
(async()=>{for(const channel of ["chrome","msedge"]) for(const width of [1280,390]) await run(channel,width);})().catch(e=>{console.error(e);process.exitCode=1;});
