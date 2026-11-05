// Add a component: write render(block) returning an element, then register it here.
import * as basic from "./basic.js";
import { flow } from "./flow.js";
import { graph } from "./graph.js";
export const blocks = { ...basic, flow, graph };
