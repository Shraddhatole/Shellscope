## Ownership network

**Method.** Glasgow (postcode area G): a graph of companies, their registered addresses and their owners (PSCs; people only as hashed IDs). UK-wide: a directed graph of company → company ownership from corporate PSC records. Measures: degree, PageRank, Louvain communities, ownership loops (strongly connected components) and chain depth (longest path in the condensed DAG). Notebook: `notebooks/08_network.ipynb`.

**Findings** (fill in with numbers):
1. Shared addresses: _… of … Glasgow companies sit in one large connected group; … addresses host 10+ companies._
2. Ownership loops: _… UK companies are in ownership loops; their average risk score is … vs … for the rest._
3. Communities: _the riskiest Glasgow community (20+ companies) averages … flags vs … for Glasgow overall._

![Largest Glasgow community](reports/figures/net_largest_community.png)
![Ownership loop](reports/figures/net_community_with_cycle.png)

**Caveat.** Network links show shared addresses or owners, not wrongdoing: formation agents legitimately register thousands of companies at one address, and group structures legitimately create chains. Live register only (dissolved companies missing); people matched by name + birth month, which can merge different people.
