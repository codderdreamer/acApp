import headers from '../../Services/headers.json'
import endpoints from '../../Endpoints.json'
import { post } from '../../Services/client'
import { ILoginUser } from './models'

const config = headers.content_type.application_json

export const LoginService = (userInfo: ILoginUser) => {
  return post(endpoints.LOGIN, userInfo, config)
}
