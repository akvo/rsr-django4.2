import React from 'react'
import classNames from 'classnames'
import { Badge } from 'antd'
import { isIndicatorHasStatus } from '../modules/results/filters'

const BadgeText = ({ color, children }) => (
  <small style={{ fontWeight: 'bold', color }}>
    {children}
  </small>
)

export const IndicatorItem = ({ selected, indicator, ...props }) => {
  const isRevision = isIndicatorHasStatus(indicator)
  const isDraft = isIndicatorHasStatus(indicator, 'D')
  const isSubmitted = isIndicatorHasStatus(indicator, 'P')
  const isApproved = isIndicatorHasStatus(indicator, 'A')
  const color = (isRevision && !isSubmitted) ? 'red' : isDraft ? 'yellow' : isSubmitted ? 'blue' : isApproved ? 'green' : 'gray'
  const badges = {
    red: {
      color: '#f5222d',
      text: <BadgeText color="#f5222d">DECLINED</BadgeText>
    },
    yellow: {
      color: '#fadb14',
      text: <BadgeText color="#ccb30a">DRAFT</BadgeText>
    },
    blue: {
      color: '#1890ff',
      text: <BadgeText color="#1890ff">SUBMITTED</BadgeText>
    },
    green: {
      color: '#52c41a',
      text: <BadgeText color="#52c41a">APPROVED</BadgeText>
    },
    gray: {
      color: '#d9d9d9',
      text: <BadgeText color="#a7a5a5">NO STATUS YET</BadgeText>
    }
  }
  return (
    <li
      className={classNames({
        selected,
        declined: color === 'red',
        draft: color === 'yellow',
        submitted: color === 'blue',
        approved: color === 'green'
      })}
      {...props}
    >
      <Badge {...badges[color]} />
      <h5>{indicator?.title}</h5>
    </li>
  )
}
