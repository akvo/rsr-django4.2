import React from 'react'
import moment from 'moment'
import { Typography } from 'antd'

const { Text } = Typography

const Author = ({
  userDetails,
  createdAt
}) => (
  <>
    <Text strong>{userDetails ? userDetails.firstName : ''} {userDetails ? userDetails.lastName : ''}</Text>
    <br />
    {(userDetails && userDetails.approvedOrganisations.slice(0, 1).length > 0) && (
      <>
        <Text>{userDetails.approvedOrganisations[0].name}</Text>
        <br />
      </>
    )}
    <Text>{createdAt ? moment(createdAt, 'YYYY-MM-DD').format('DD-MMM-YYYY') : ''}</Text>
  </>
)

export default Author
