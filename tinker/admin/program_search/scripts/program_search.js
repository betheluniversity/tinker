var ReactDOM = require('react-dom');


var Loader = require('react-loader');
var Modal = require('react-bootstrap').Modal;
var Button = require('react-bootstrap').Button;
var ButtonToolbar = require('react-bootstrap').ButtonToolbar;

var ProgramResult = React.createClass({
    handleClick: function(e) {
        if (typeof this.props.onClick === 'function') {
            this.props.onClick(this.props.tag);
        }
    },
    render: function() {
        var tag = this.props.tag;
        return (
            <tr onClick={this.handleClick} key={tag['id']}>
                <td>{tag['key']}</td>
                <td>{tag['tag']}</td>
                <td>{tag['outcome'] ? 'X': ''}</td>
                <td>{tag['topic'] ? 'X': ''}</td>
                <td>{tag['other'] ? 'X': ''}</td>
            </tr>
        );
    }
});

var ProgramSearch = React.createClass({

  // sets initial state
  getInitialState: function(){
    return { tagString: '', keyString: '', tags: [], showModal: false, currentTag: '', loaded: true };
  },

  componentDidMount: function() {
    this.serverRequest = $.get(this.props.source, function (result) {
      var tags = result['tags'];
      this.setState({tags: tags});
    }.bind(this));
  },

  // sets state, triggers render method
  handleTagChange: function(event){
    this.setState({tagString:event.target.value});
  },

  // sets state, triggers render method
  handleKeyChange: function(event){
    this.setState({keyString:event.target.value});
  },

  close() {
    this.setState({ showModal: false });
  },

  open() {
    this.setState({ showModal: true });
  },

  handleClick: function(tag) {
    this.open();
    this.setState({ currentTag: tag });
  },

  deleteCurrentTag: function(){
    this.setState({ loaded: false });
    var id = this.state.currentTag['id'];
    var url = 'http://127.0.0.1:5000/admin/programsearch/' + id;
      $.ajax({
          context: this,
          id: id,
          url: url,
          method: 'DELETE',
          data: { tag_id: id }
        }).success(function(){
          var tags = this.state.tags.filter(function(tag){
            return tag['id'] !== id;
          });
          this.setState({ tags: tags });
          this.setState({ loaded: true });
      });
    this.close();
  },

  render: function() {

    var tags = this.state.tags;
    var tagString = this.state.tagString.trim().toLowerCase();
    var keyString = this.state.keyString.trim().toLowerCase();

    if(tagString.length > 0 || keyString.length > 0){
        tags = tags.filter(function(tag){
            var ks = tag['key'].toLowerCase().match( keyString );
            var ts = tag['tag'].toLowerCase().match( tagString );
            if (ks && ts ){
                return tag;
            }
      });
    }

    return (
      <div>
        <label for="tag">Filter Tag:</label>
        <input type="text" name="tag" value={this.state.tagString} onChange={this.handleTagChange} placeholder="Filter Tag" />
        <label for="key">Filter Key:</label>
        <input type="text" name="key" value={this.state.keyString} onChange={this.handleKeyChange} placeholder="Filter Key" />
        <table>
            <thead>
                <tr>
                    <th>Key</th>
                    <th>Tag</th>
                    <th>Outcome</th>
                    <th>Topic</th>
                    <th>Other</th>
                </tr>
            </thead>
            <tbody>
                {
                    tags.map(function(tag){
                        return <ProgramResult key={tag['id']} tag={tag} onClick={this.handleClick} />
                    }, this)
                }
            </tbody>
        </table>
        <Modal show={this.state.showModal} onHide={this.close}>
          <Modal.Header closeButton>
            <Modal.Title>Delete Tag "{this.state.currentTag['tag']}"</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <ButtonToolbar>
                <Button bsStyle="danger" onClick={this.deleteCurrentTag}>Delete</Button>
                <Button bsStyle="primary" onClick={this.close}>Cancel</Button>
            </ButtonToolbar>
          </Modal.Body>
        </Modal>
        <Loader loaded={this.state.loaded}/>
      </div>
    )
  }
});

ReactDOM.render(
  <ProgramSearch source="http://127.0.0.1:5000/admin/programsearch/all"/>,
  document.getElementById('main')
);