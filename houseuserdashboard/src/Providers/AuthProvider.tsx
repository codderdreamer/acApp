import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Outlet, useNavigate } from "react-router-dom";
import { RootState } from "../Stores/reducers";

const AuthProvider = () => {
  let navigate = useNavigate();
  let User = useSelector((state: RootState) => state.user);
  let dispatch: any = useDispatch();

  // Kullanicinin giris yapip yapmadigi kontrol edilmeli
  useEffect(() => {}, [User.data, User.error]);

  return <Outlet />;
};

export default AuthProvider;
