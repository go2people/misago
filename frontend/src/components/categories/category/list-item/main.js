// jshint ignore:start
import React from 'react';
import Description from './description';
import Icon from './icon';
import {Subscription} from "../../../thread/toolbar-bottom";
import SubscriptionFull from 'misago/components/threads-list/thread/subscription/full';

export default function({ category }) {
  return (
    <div className="col-xs-12 col-sm-6 col-md-6 category-main">
      <div className="media">
        <div className="media-left">
          <Icon category={category} />
        </div>
        <div className="media-body">
          <h4 className="media-heading">
            <a href={category.url.index}>
                { category.name }
            </a>
          </h4>
          {/*<Subscription {...category} />*/}
          <SubscriptionFull
          thread={category}
          />
          <Description category={category} />
        </div>
      </div>
    </div>
  );
}