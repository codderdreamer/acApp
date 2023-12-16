import { combineReducers } from "redux";
import accountReducer from "./Reducers/Account";

const rootReducer = combineReducers({
  user: accountReducer,
});

export type RootState = ReturnType<typeof rootReducer>;

export default rootReducer;
