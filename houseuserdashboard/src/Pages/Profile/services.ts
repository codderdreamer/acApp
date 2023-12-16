import headers from '../../Services/headers.json'
import endpoints from '../../Endpoints.json'
import { patch } from '../../Services/client'
import { IChangePassword } from './models'

const config = headers.content_type.application_json

export const ChangePasswordService = (data: IChangePassword) => {
  return patch(endpoints.CHANGEPASSWORD, data, config)
}
