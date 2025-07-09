# MCP PostgreSQL Playground Specification v1

## Overview
This specification defines the implementation of a PostgreSQL MCP (Model Context Protocol) playground for testing and demonstrating AI-powered database interactions with Claude Code.

## Current Environment Analysis

### PostgreSQL Setup
- **Version**: PostgreSQL 14.18 (Homebrew)
- **User**: kimomaxmac
- **Host**: localhost (default port 5432)
- **Existing databases**: bashacore_dev, pgvector_test, postgres, template0, template1
- **Status**: Running and accessible

### Development Environment
- **Node.js**: v24.1.0
- **npm**: 11.3.0
- **Platform**: macOS (aarch64-apple-darwin24.4.0)

## Database Design

### Database Creation
- **Name**: `mcp_playground`
- **Owner**: kimomaxmac
- **Purpose**: Isolated environment for MCP testing

### Schema Design

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    user_type VARCHAR(20) DEFAULT 'customer'
);
```

#### Products Table
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(50),
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);
```

#### Orders Table
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_date TIMESTAMP,
    delivery_address TEXT
);
```

#### Order Items Table
```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL
);
```

#### Reviews Table
```sql
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT false
);
```

## Sample Data Structure

### Users (15 records)
- Mix of customer and admin users
- Realistic names and email addresses
- Various creation dates over past 6 months
- Mix of active/inactive users

### Products (20 records)
- Categories: Electronics, Books, Clothing, Home, Sports
- Price range: $9.99 - $999.99
- Varying stock quantities
- Realistic product descriptions

### Orders (30 records)
- Status distribution: pending (20%), processing (15%), shipped (35%), delivered (25%), cancelled (5%)
- Order dates spanning last 3 months
- Realistic total amounts based on product prices

### Order Items (75 records)
- Multiple items per order (average 2.5 items)
- Quantities typically 1-3 per item
- Prices matching product prices at time of order

### Reviews (40 records)
- Rating distribution: 5-star (40%), 4-star (30%), 3-star (20%), 2-star (7%), 1-star (3%)
- Mix of detailed and brief comments
- About 50% verified reviews

## MCP Server Configuration

### Installation
```bash
npm install -g @modelcontextprotocol/server-postgres
```

### Configuration
```bash
# Connection string format
postgresql://kimomaxmac@localhost:5432/mcp_playground

# Claude Code MCP configuration
claude mcp add postgres-playground @modelcontextprotocol/server-postgres --connection-string "postgresql://kimomaxmac@localhost:5432/mcp_playground"
```

### Security Considerations
- Read-only access for MCP server
- No write/modify permissions
- Local database connection only
- No sensitive data in sample dataset

## Test Scenarios

### Basic Queries
1. **User Analysis**
   - "Show me all active users"
   - "Find users who joined in the last 30 days"
   - "List users by registration date"

2. **Product Insights**
   - "Show me products with low stock (< 10)"
   - "Find the most expensive products in each category"
   - "List products that haven't been ordered"

3. **Order Analysis**
   - "Show me recent orders with their total amounts"
   - "Find orders with more than 3 items"
   - "Calculate average order value by month"

### Complex Queries
1. **Customer Behavior**
   - "Who are our top 5 customers by total order value?"
   - "Show customers who haven't ordered in 60 days"
   - "Find users who have written reviews but never ordered"

2. **Sales Analytics**
   - "What's the monthly revenue trend?"
   - "Which products generate the most revenue?"
   - "Show order status distribution by month"

3. **Inventory Management**
   - "Products that need restocking (stock < 5)"
   - "Best-selling products by category"
   - "Products with highest average rating"

### Advanced Scenarios
1. **Multi-table Joins**
   - "Show user details with their order history"
   - "Product performance with reviews and sales data"
   - "Customer lifetime value analysis"

2. **Aggregation Queries**
   - "Monthly sales report with product breakdown"
   - "User engagement metrics"
   - "Product rating trends over time"

## Implementation Steps

### Phase 1: Database Setup
1. Create `mcp_playground` database
2. Execute schema creation SQL
3. Insert sample data
4. Verify data integrity with test queries

### Phase 2: MCP Server Installation
1. Install MCP server package globally
2. Configure connection string
3. Add to Claude Code MCP configuration
4. Test basic connectivity

### Phase 3: Integration Testing
1. Test schema inspection through MCP
2. Execute sample queries via Claude
3. Verify read-only access restrictions
4. Test complex multi-table queries

### Phase 4: Documentation
1. Create usage examples
2. Document common query patterns
3. Add troubleshooting guide
4. Create demo scenarios

## Success Criteria

### Technical Requirements
- [x] PostgreSQL database created and accessible
- [ ] All tables created with proper relationships
- [ ] Sample data inserted (100+ total records)
- [ ] MCP server installed and configured
- [ ] Claude Code integration working
- [ ] Read-only access confirmed

### Functional Requirements
- [ ] Claude can inspect database schema
- [ ] Basic SELECT queries work through MCP
- [ ] Complex JOIN queries execute successfully
- [ ] Aggregation and analytical queries function
- [ ] Error handling works for invalid queries
- [ ] Performance acceptable for demo purposes

### User Experience
- [ ] Natural language to SQL translation works
- [ ] Query results are properly formatted
- [ ] Claude provides helpful query suggestions
- [ ] Error messages are clear and actionable
- [ ] Documentation is comprehensive and clear

## Expected Outcomes

### Immediate Benefits
- Functional MCP PostgreSQL playground
- Understanding of MCP architecture
- Hands-on experience with AI-database integration
- Reusable setup for future projects

### Learning Opportunities
- MCP protocol understanding
- AI-powered data analysis workflows
- Database query optimization through AI
- Integration patterns for AI tools

### Future Extensions
- Additional MCP servers (GitHub, filesystem)
- More complex database schemas
- Real-time data integration
- Custom MCP server development

## Troubleshooting Guide

### Common Issues
1. **Connection Errors**
   - Verify PostgreSQL is running
   - Check connection string format
   - Confirm database exists

2. **Permission Issues**
   - Ensure user has database access
   - Verify read permissions on tables
   - Check MCP server configuration

3. **Query Failures**
   - Validate SQL syntax
   - Check table/column names
   - Verify data types in conditions

### Debugging Steps
1. Test direct psql connection
2. Verify MCP server status
3. Check Claude Code MCP configuration
4. Review error logs
5. Test with simplified queries

## Version History
- **v1.0**: Initial specification with basic e-commerce schema and MCP setup